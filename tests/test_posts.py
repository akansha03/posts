import pytest
from app import schema
# Practice : setup the order to get the lowest id for the last assertion to work

def test_get_all_posts(authorized_client, test_create_posts):
    res = authorized_client.get("/posts/")
    def validate(post):
        return schema.PostOut(**post)
    post_map = map(validate, res.json())
    posts = list(post_map)

    assert len(res.json()) == len(test_create_posts)
    assert res.status_code == 200
    #assert posts[0].Post.id == test_create_posts[0].id

def test_unauthorized_user_get_all_posts(client, test_create_posts):
    res = client.get("/posts/")
    assert res.status_code == 401

def test_unauthorized_user_get_one_posts(client, test_create_posts):
    res = client.get(f"/posts/{test_create_posts[0].id}")
    assert res.status_code == 401

def test_get_one_post_not_exist(authorized_client, test_create_posts):
    res = authorized_client.get("/posts/999")
    assert res.status_code == 404

def test_get_one_post(authorized_client, test_create_posts):
    res = authorized_client.get(f"/posts/{test_create_posts[0].id}")
    post = schema.PostOut(**res.json())
    assert post.Post.id == test_create_posts[0].id
    assert post.Post.title == test_create_posts[0].title
    assert post.Post.content == test_create_posts[0].content

@pytest.mark.parametrize("title, content, published", [("new title 1", "new_content", True), ("new title 2", "new_content 2", False), ("new title 3", "new_content 3", True)])
def test_create_post(authorized_client, test_user, test_create_posts, title, content, published):
    res = authorized_client.post("/posts/", json={"title": title, "content": content, "published": published})
    created_post = schema.Post(**res.json())
    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == test_user['id']

def test_create_post_default_published_true(authorized_client, test_user, test_create_posts):
    res = authorized_client.post("/posts/", json={"title": "demo title", "content": "demo content"})
    created_post = schema.Post(**res.json())
    assert res.status_code == 201
    assert created_post.title == "demo title"
    assert created_post.content == "demo content"
    assert created_post.published == True
    assert created_post.owner_id == test_user['id']

def test_unauthorized_user_get_all_posts(client, test_create_posts):
    res = client.post("/posts/", json={"title": "demo title", "content": "demo content"})
    assert res.status_code == 401

def test_unauthorized_user_delete_post(client, test_user, test_create_posts):
    res = client.delete(f"/posts/{test_create_posts[0].id}")
    assert res.status_code == 401

def test_delete_post_success(authorized_client, test_user, test_create_posts):
    res = authorized_client.delete(f"/posts/{test_create_posts[0].id}")
    assert res.status_code == 204

def test_delete_post_not_exist(authorized_client, test_user, test_create_posts):
    res = authorized_client.delete("/posts/90000")
    assert res.status_code == 404 

def test_delete_other_user_post(authorized_client, test_user, test_create_posts):
    res = authorized_client.delete(f"/posts/{test_create_posts[2].id}")
    assert res.status_code == 403

def test_update_post(authorized_client, test_user, test_create_posts):
    data = {
        "title" : "updated title",
        "content" : "updated content",
        "id" : test_create_posts[0].id
    }

    res = authorized_client.put(f"/posts/{test_create_posts[0].id}", json=data)
    updated_post = schema.Post(**res.json())
    assert res.status_code == 200
    assert updated_post.title == data['title']
    assert updated_post.content == data['content']

def test_update_other_user_post(authorized_client, test_user, test_user_2, test_create_posts):
    data = {
        "title" : "updated title",
        "content" : "updated content",
        "id" : test_create_posts[2].id
    }
    res = authorized_client.put(f"/posts/{test_create_posts[2].id}", json=data)
    assert res.status_code == 403

def test_unauthorized_user_update_post(client, test_user, test_create_posts):
    res = client.put(f"/posts/{test_create_posts[0].id}")
    assert res.status_code == 401

def test_update_post_not_exist(authorized_client, test_user, test_create_posts):
    data = {
        "title" : "updated title",
        "content" : "updated content",
        "id" : test_create_posts[2].id
    }
    res = authorized_client.put("/posts/90000", json=data)
    assert res.status_code == 404 
