# Instructions

docker build -t server -f Dockerfile ./

docker compose up

## Register user request
```
curl --location --request POST 'http://127.0.0.1:8000/register' \
--header 'Content-Type: application/json' \
--data-raw '{ "username": "testuser", "password": "password" }'
```
## Login
```
curl --location --request GET 'http://127.0.0.1:8000/login' \
--header 'Content-Type: application/json' \
--data-raw '{ "username": "testuser", "password": "1234" }'
```
Response:
```
{
    "username": "testuser2",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3R1c2VyMiJ9.W1Q3prXnDU8KLC3qw8JBp7bwkTdT3bYAEF7q8ANlEGw",
    "_id": "638315b9dba5adc8dd4ed239"
}
```
Set token for authorization header (Bearer)

## Transcribe a file:
```
curl --location --request POST 'http://127.0.0.1:8000/upload-transcribe' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3R1c2VyMiJ9.W1Q3prXnDU8KLC3qw8JBp7bwkTdT3bYAEF7q8ANlEGw' \
--form 'file=@"/deepspeech/audio/8455-210777-0068.wav"'
```

## Get all transcribes
```
curl --location --request GET 'http://127.0.0.1:8000/transcribes' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3R1c2VyMiJ9.W1Q3prXnDU8KLC3qw8JBp7bwkTdT3bYAEF7q8ANlEGw'
```