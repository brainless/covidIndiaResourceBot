# Covid-19 India Resource Bot (cirb)
`covidIndiaResourceBot`

### API backend to generate contextual conversations for chats with folks looking for resources in the Covid-19 crisis in India

## Usage

This is a simple Python based API that generates texts depending on the context of the current user in the chat.
The API uses the current user's phone number as the identifier at all times.

API base URL: `https://cirb.dwata.com/api/1`

_Note_: This current API is versioned in case we introduce any breaking changes for other consumers.

## API Request
The typical API request would look like:

`HTTP POST /api/1/chat`
```json
{
  "phone": "+911234512345",
  "message": "Hello, I am looking for help with Oxygen",
  "created_by": "user",
  "created_at": "2021-05-03T13:56:20+00:00"
}
```

All the fields are self-explanatory. Here `created_by` is an enumeration of `["user", "operator"]`.

Ideally `operator` (our volunteers) created messages will not need to be addressed, but this is kept in case there is need for the bot to intervene after volunteer has joined in the conversation.

## API Response
The API response would itself be a JSON payload like:

```json
{
  "phone": "+911234512345",
  "message": "Sure, can you please tell me what is your city?",
  "tags": ["oxygen"]
}
```

## Ideas
The API tries to stay away from the context that the consumer of the API may have, for example ID of operator or other tags that the consumer (DelightChat UI) may have added.
It is the job of the consumer to see if tags can be applied or not.