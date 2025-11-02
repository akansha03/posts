import pytest
from app import models

# User cannot vote on his own post and test it first

@pytest.fixture
def test_vote(test_create_posts, session, test_user):
    new_vote = models.Votes(post_id=test_create_posts[2].id, user_id=test_user['id'])
    session.add(new_vote)
    session.commit()

def test_vote_on_post(authorized_client, test_create_posts):
    res = authorized_client.post("/vote/", json={"post_id": test_create_posts[2].id, "dir" : 1})
    assert res.status_code == 201

def test_vote_twice_post(authorized_client, test_create_posts):
    res = authorized_client.post("/vote/", json={"post_id" : test_create_posts[2].id, "dir" : 1})
    assert res.status_code == 201 # update it to 409 when check on user not able to vote it's own post is implemented

def test_delete_vote(authorized_client, test_create_posts, test_vote):
    res = authorized_client.post("/vote/", json={"post_id" : test_create_posts[2].id, "dir" : 0})
    assert res.status_code == 201

def test_delete_vote_non_exist(authorized_client, test_create_posts):
    res = authorized_client.post("/vote/", json={"post_id" : test_create_posts[2].id, "dir" : 0})
    assert res.status_code == 404

def test_vote_post_non_exist(authorized_client, test_create_posts):
    res = authorized_client.post("/vote/", json={"post_id": 9000, "dir": 1})
    assert res.status_code == 404

def test_vote_unauthorized_user(client, test_create_posts):
    res = client.post("/vote/", json={"post_id" : test_create_posts[2].id, "dir" : 1})
    assert res.status_code == 401

