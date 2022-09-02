import json
import boto3
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO


def get_image_name(html_body):
    body = BeautifulSoup(html_body, 'html.parser')
    image_tag = body.find('meta', property='og:image')
    image_name = image_tag['content'].split('/')[-1]
    return image_name


def resize_image(image):
    sizeX = image.size[0]
    sizeY = image.size[1]
    if sizeX > 300:
        image.thumbnail((299, sizeY))


def create_thumbnail(s3_client, s3_bucket, original_image, path):
    image_object = s3_client.get_object(
        Bucket=s3_bucket, Key=original_image)
    image = Image.open(BytesIO(image_object['Body'].read()))
    resize_image(image)
    file_object = BytesIO()
    image.save(file_object, 'png')
    file_object.seek(0)
    s3_client.put_object(Body=file_object, Bucket=s3_bucket,
                         Key=path, ContentType=image_object['ContentType'])


def object_exists(s3_client, s3_bucket, path):
    try:
        s3_client.head_object(Bucket=s3_bucket, Key=path)
        return True
    except:
        return False


def lambda_handler(event, context):

    request = event['Records'][0]['cf']['request']

    if 'api/rich_link' in request['uri']:
        s3_bucket = 'cambiatus-uploads'
        s3_image_path = 'cambiatus-uploads/'
        s3_thumb_path = 'cambiatus-uploads/thumbnails/'
        s3_client = boto3.client('s3')

        image_name = get_image_name(request['body'])

        if not object_exists(s3_client, s3_bucket, s3_thumb_path+image_name):
            create_thumbnail(s3_client, s3_bucket, s3_image_path +
                             image_name, s3_thumb_path+image_name)

        request['body'] = request['body'].replace(s3_image_path, s3_thumb_path)

    return {
        'statusCode': 200,
        'body': json.dumps(request['body'])
    }
