# Engagement Bot for Uni

To setup the bot configure the variables in `GetCreds()` function in `main.py`.

Note that you need to download the most recent version of [ChromeDriver](https://sites.google.com/chromium.org/driver/) that supports your chrome version (likely version 96), and place the executable into the same folder as `main.py`. You may also have to add it to the PATH if the same directory doesn't work.

There is also a scheduler that can be enabled and configured through the arguments.

See all available arguments with `python main.py -h`.

This bot will:
- Login
- Access a few random canvas resources
- Logout
