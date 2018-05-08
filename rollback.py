import os, tweepy, inspect, hashlib, time

consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

while True:
    hashtag = "#RollBackBITSPilaniFeeHike"
    tweetLanguage = ""

    # Number retweets per time
    num = 20

    # blacklisted users and words
    userBlacklist = []
    wordBlacklist = ["RT", u"♺"]

    # build savepoint path + file
    hashedHashtag = hashlib.md5(hashtag.encode('ascii')).hexdigest()
    last_id_filename = "last_id_hashtag_%s" % hashedHashtag
    rt_bot_path = os.path.dirname(os.path.abspath(__file__))
    last_id_file = os.path.join(rt_bot_path, last_id_filename)

    # create bot
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # retrieve last savepoint if available
    try:
        with open(last_id_file, "r") as file:
            savepoint = file.read()
    except IOError:
        savepoint = ""
        print("No savepoint found. Bot is now searching for results")

    # search query
    timelineIterator = tweepy.Cursor(api.search, q=hashtag, since_id=savepoint, lang=tweetLanguage).items(num)
    print("Searched...")

    # list of status IDs
    timeline = []
    for status in timelineIterator:
        timeline.append(status)


    try:
        last_tweet_id = timeline[0].id
    except IndexError:
        last_tweet_id = savepoint

    # filter backlisted words
    timeline = filter(lambda status: not any(word in status.text.split() for word in wordBlacklist), timeline)
    timeline = filter(lambda status: status.author.screen_name not in userBlacklist, timeline)
    timeline = list(timeline)
    timeline.reverse()

    tw_counter = 0
    err_counter = 0

    # iterate the timeline
    for status in timeline:
        try:
            print("(%(date)s) %(name)s: %(message)s\n" % \
                  {"date": status.created_at,
                   "name": status.author.screen_name.encode('utf-8'),
                   "message": status.text.encode('utf-8')})
 
            # retweet
            api.retweet(status.id)
            # reply
            api.update_status("@narendramodi @HRDMinistry @ShashiTharoor #BITSAgainstFeeHike @"+status.author.screen_name,status.id)
            tw_counter += 1
            
        except tweepy.error.TweepError as e:
            # just in case tweet got deleted in the meantime or already retweeted
            err_counter += 1
            print(e)
            continue

    print("Finished. %d Tweets retweeted, %d errors occured." % (tw_counter, err_counter))

    # write last retweeted tweet id to file
    with open(last_id_file, "w") as file:
        file.write(str(last_tweet_id))

    time.sleep(120)
