from bs4 import BeautifulSoup
import os
import requests
import boto3
import timeit

# Environment variables
TABLE_NAME = os.environ['AWS_DYNAMO_TABLE_NAME']
STORIES_SOURCE = os.environ['STORIES_SOURCE']
STORIES_COUNT = int(os.environ['STORIES_COUNT'])

# AWS objects
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)


def retrieve_data(url):
    source = requests.get(url)
    retrieved_data = BeautifulSoup(source.text, 'lxml')
    return retrieved_data


def create_fable(index, data):
    title = data.find('h1').text
    quote = data.find('blockquote').text
    paragraphs = map(lambda p: p.text, data.find_all('p'))

    # The `&` sign can not be read by Alexa
    title = title.replace('&', 'and')

    return {
        'id': index,
        'title': title,
        'quote': quote,
        'story': '<break/>'.join(paragraphs)
    }


def scan_item(index):
    print()
    # Stories start at `/002.html`
    file = '{:03d}.html'.format(index + 2)
    url = os.path.join(STORIES_SOURCE, file)
    print('Scanning item: \'{}\'.'.format(file))

    network_request_timer_start = timeit.default_timer()
    data = retrieve_data(url)
    fable = create_fable(index, data)
    network_request_time = (timeit.default_timer() - network_request_timer_start) * 1000
    print('Retrieved fable: \'{}\' in {:.2f}ms.'.format(fable['title'], network_request_time))

    aws_request_timer_start = timeit.default_timer()
    table.put_item(Item=fable)
    aws_request_time = (timeit.default_timer() - aws_request_timer_start) * 1000
    print('Uploaded fable to AWS DynamoDB in {:.2f}ms.'.format(aws_request_time))


def main():
    main_timer_start = timeit.default_timer()
    print('Scan initiated.')

    for index in range(0, STORIES_COUNT):
        scan_item(index)

    total_time_elapsed = timeit.default_timer() - main_timer_start
    print('Scan completed in {:.1f}s.'.format(total_time_elapsed))


if __name__ == '__main__':
    main()
