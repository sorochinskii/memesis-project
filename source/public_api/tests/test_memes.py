import json

import httpx
import pytest
from asyncmock import AsyncMock
from httpx import AsyncClient, Response
from PIL import Image


class TestMemes:

    shared = {}

    async def test_meme_create(self, test_client: AsyncClient, mocker):
        Image.new(
            mode=pytest.image_1.mode,
            size=pytest.image_1.size).save(pytest.image_1.name)
        patch_private_response = httpx.Response(
            status_code=httpx.codes.CREATED, json={'name': pytest.meme_1.name})
        mocker.patch('v1.endpoints.memes.post_upload_file',
                     AsyncMock(return_value=patch_private_response))
        payload = {
            'meme': json.dumps(
                {'name': pytest.meme_1.name, 'text': pytest.meme_1.text})}
        files = {'file': (pytest.filename_1,
                          open(pytest.filename_1, 'rb'),
                          'image/jpg')}

        response = await test_client.post('/v1/memes', data=payload,
                                          files=files)

        TestMemes.shared['created_id'] = response.json().get('id')
        created_name = response.json().get('name')
        assert created_name == pytest.meme_1.name

    async def test_meme_get(self, test_client: AsyncClient, mocker):
        id = TestMemes.shared.get('created_id')
        mocker.patch('v1.endpoints.memes.get_presigned_url',
                     AsyncMock(return_value=pytest.filename_1))

        response = await test_client.get(f'/v1/memes/{id}')

        TestMemes.shared['url'] = response.json().get('url')
        TestMemes.shared['token'] = response.json().get('token')
        assert response.json().get('name') == pytest.meme_1.name

    async def test_get_image(self, test_client: AsyncClient, mocker):
        async def iterfile():
            with open(pytest.filename_1, mode="rb") as file:
                while (chunk := file.read(1024)):
                    yield chunk
        token = TestMemes.shared['token']
        image_response = Response(status_code=httpx.codes.OK,
                                  content=iterfile())
        mocker.patch('v1.endpoints.memes.get_image_with_url',
                     AsyncMock(return_value=image_response))

        response = await test_client.get(f'/v1/memes/get_image/{token}')

        file = open(pytest.filename_1, mode='rb').read()
        response_file = response.read()
        assert file == response_file

    async def test_meme_replace(self, test_client: AsyncClient, mocker):
        filename = 'image_2.png'
        Image.new(mode="RGB", size=(300, 300)).save(filename)
        meme_data = json.dumps(
            {'id': TestMemes.shared.get('created_id'),
             'name': pytest.meme_2.name})
        payload = {'meme': meme_data}
        files = {'file': (pytest.filename_2,
                          open(pytest.filename_2, 'rb'),
                          'image/png')}

        patch_private_response = httpx.Response(
            status_code=httpx.codes.CREATED, json={'name': pytest.meme_2.name})
        mocker.patch('v1.endpoints.memes.post_upload_file',
                     AsyncMock(return_value=patch_private_response))

        item_id = TestMemes.shared.get('created_id')
        response_replaced = await test_client.put(f'/v1/memes/{item_id}',
                                                  data=payload,
                                                  files=files)

        updated_name = response_replaced.json().get('name')
        updated_id = response_replaced.json().get('id')

        assert updated_name == pytest.meme_2.name
        assert updated_id == TestMemes.shared.get('created_id')

    async def test_delete_meme(self, test_client: AsyncClient, mocker):
        id = TestMemes.shared.get('created_id')
        patch_delete_image = httpx.Response(status_code=httpx.codes.OK,
                                            json={'id': id})
        mocker.patch('v1.endpoints.memes.delete_image_from_s3',
                     AsyncMock(return_value=patch_delete_image))

        deleted_id_response = await test_client.delete(f'/v1/memes/{id}')

        assert id == deleted_id_response.json()
