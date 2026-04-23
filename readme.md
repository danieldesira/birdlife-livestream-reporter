# Livestream Reporter

## Setup

Clone the following Git repository:
`git clone https://github.com/danieldesira/birdlife-lifestream-reporter`

The following environment variables are required for email
functionality to work:

- `MAIL_HOST`
- `MAIL_PORT`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_RECIPIENTS`

Build the Docker image using:
`docker compose up --build`

## Use

To add or remove streams, please modify
`youtube_streams.json`. Add an object with the following structure:

```json
{
    "name": "Zurrieq Primary",
    "url": "https://bit.ly/zpbtwc"
},
```

`name`: The name of the livestream as to be shown in the report.

`url`: `bit.ly` link redirecting to the stream on YouTube.

## Implementation

The livestream validation algorithm works as follows:

1. We try to open the stream. `False` is returned immediately in case of failure.
2. If it succeeds, we get 3 consecutive frames.
3. We convert each frame to a hash.
4. We compare the hashes and return `True` if any of the differences is over 0.
5. Otherwise, we return `False`.

Libraries used:

- `Streamlink` to access Youtube livestreams
- `Pillow` to work with images
- `Imagehash` to create hashes from images
