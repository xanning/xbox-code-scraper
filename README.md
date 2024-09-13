# xbox-code-scraper
A request based Python tool to scrape XBOX friend invite codes from mailpass list

# WARNING:

This will probably skip a lots of accounts (possibly the ones with "Your security info change pending", i don't know why. It's just weird. Use MSMC.

# Heavily skidded from MSMC because i have no idea how to code a request based tool.

Special thanks to Copilot for making my code into what i actually want.

# Threading? Proxy?

No. There's no threading nor proxy, if you wanna add, it shouldnt be that hard. 

# How to use

put your mail:pass list on combos.txt, run the scraper.py. Thats all. Valid gamepass accounts will be saved to their own txts, codes on codes.txt
Note, this does NOT act as a MC checker too, no, use MSMC for that. It'll say "other" to every MC hits and invalids

# Note

This assumes most of the combos.txt are hits. Tool is made for finding gamepass accs and extracting codes from them, not wholeheartedly checking valid mc.

If some are invalid, it will still work but since tool is proxyless it would cause you to get ratelimited. Probably. I dont know. Have my code and do what you want

# In addition

Yes, MSMC does have a code scraper but i pasted these from there and made this because MSMC just made me have a bad time because i'm proxyless checking and thing trying to check every single thing like balance and all.
