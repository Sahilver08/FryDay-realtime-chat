import requests

# Step 1: Register a user
print('=== STEP 1: Registering user ===')
register_data = {
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'securepass123'
}
register_response = requests.post('http://localhost:8000/api/accounts/register/', json=register_data)
print(f'Status: {register_response.status_code}')
print(f'Response: {register_response.json()}')
print()

# Step 2: Get access token
print('=== STEP 2: Getting access token ===')
login_data = {
    'username': 'testuser',
    'password': 'securepass123'
}
login_response = requests.post('http://localhost:8000/api/login/', json=login_data)
print(f'Status: {login_response.status_code}')
token_data = login_response.json()
print(f'Response: {token_data}')
access_token = token_data.get('access')
print()

# Step 3: Access profile with token
print('=== STEP 3: Accessing profile with token ===')
headers = {'Authorization': f'Bearer {access_token}'}
profile_response = requests.get('http://localhost:8000/api/accounts/profile/', headers=headers)
print(f'Status: {profile_response.status_code}')
print(f'Response: {profile_response.json()}')
