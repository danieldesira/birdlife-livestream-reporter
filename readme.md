# Livestream Reporter

## Setup

Clone the following Git repository:
`git clone https://github.com/danieldesira/birdlife-livestream-reporter`

The following environment variables are required for email
functionality to work:

- `MAIL_HOST`
- `MAIL_PORT`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_RECIPIENTS`

Moreover, `YOUTUBE_API_KEY` is mandatory as it is part of the process.

Install the dependencies as follows:

1. Create virtual environment using: `py -m venv .venv`
2. Activate virtual environment. (Windows: `.venv\Scripts\Activate`, MacOS/Linux: `source .venv/bin/activate`)
3. Upgrade pip: `py -m pip install --upgrade pip`
4. Install packages: `pip install -r requirements.txt`

Run the script using: `py -m main`

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

1. We check the status from the Youtube API.
2. If the stream is `live`, we try to open the stream. Otherwise we immediately return `Offline`.
3. If it succeeds, we get 2 consecutive frames.
4. We convert each frame to a hash.
5. We compare the hashes and return `Stalled` if they are identical.
6. Otherwise, we return `Online`.

Libraries used:

- `Streamlink` to access Youtube livestreams
- `Pillow` to work with images
- `Imagehash` to create hashes from images
