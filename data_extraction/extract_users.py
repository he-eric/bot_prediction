import configparser
import praw
import json
import urllib.request
import time

config = configparser.ConfigParser()
config.read('credentials.ini')
creds = config['creds']
client = creds['client_id']
secret = creds['api_key']
username = creds['username']
password = creds['password']

reddit = praw.Reddit(user_agent='Gather user profiles (by /u/dog3421)',
                     client_id=client, client_secret=secret)

def get_normies():
    print('Get_normies()')
    last_utc = '1428624000'
    limit = 1000
    normies = []

    while len(normies) < limit:

        url = 'https://api.pushshift.io/reddit/comment/search?after=' + last_utc + '&before=1523318400&size=500'
        url = urllib.request.urlopen(url)
        contents = url.read()
        encoding = url.info().get_content_charset('utf-8')
        data = json.loads(contents.decode(encoding))

        for comment in data['data']:
            print('get ' + comment['author'])
            normies.append(comment['author'])
            last_utc = str(comment['created_utc'] + 1)

    return normies[:limit]

def scrape():
    print('Scrape()')
    bots = []
    with open("troll_accounts", 'r') as f:
        for line in f:
            user = line.split()
            username = user[0][2:]
            bots.append(username)

    normies = get_normies()

    #bot_profiles = scrape_user_profile(bots)
    normie_profiles = scrape_user_profile(normies, is_troll=False)


def scrape_user_profile(reddit_users, is_troll=True):
    print('Scrape_user_profile()')
    deleted_users = []
    profiles = {}
    for user_name in reddit_users:
        print('try ' + user_name)
        try:
            redditor = reddit.redditor(user_name)
            profiles[user_name] = {}
            profile = profiles[user_name]
            profile['comment_karma'] = redditor.comment_karma
            profile['link_karma'] = redditor.link_karma
            profile['created_utc'] = redditor.created_utc
            profile['is_troll'] = is_troll

        except Exception as e:
            print(e)
            print("Reddit account " + user_name + " has been deleted")
            deleted_users.append(user_name)
            continue

    print('Write deleted users')
    with open('deleted_users.txt', 'a') as f:
        for deleted_user in deleted_users:
            f.write(deleted_user)
            f.write(',')

    if is_troll:
        print('Write bot profiles')
        with open('bot_profiles.txt', 'w') as f:
            json.dump(profiles, f)

    else:
        print('Write normie profiles')
        with open('normie_profiles.txt', 'w') as f:
            json.dump(profiles, f)

    return profiles

def get_post_data_from_user(author, last_utc):
    url = 'https://api.pushshift.io/reddit/submission/search?after=' + last_utc \
        + '&before=1523318400&size=500&author=' + author
    web_url = urllib.request.urlopen(url)
    contents = web_url.read()
    encoding = web_url.info().get_content_charset('utf-8')
    data = json.loads(contents.decode(encoding))
    return data

def get_user_posts(author, is_bot=True):
    print('get_user_posts()')
    last_utc = '1428624000'
    created_utc = []
    num_comments = []
    score = []
    subreddit = []
    title = []
    selftext = []
    labels = []
    user = []

    # Loop through all posts between 1428624000 (4/10/2015) to 1523318400 (4/10/18)
    # These are the dates that the bots were active
    print('Get posts from ' + author)

    # Add each post to the user
    time.sleep(1)
    data = get_post_data_from_user(author, last_utc)['data']
    for post in data:

        if is_bot:
            labels.append(1)
        else:
            labels.append(0)

        try:
            sub = post['subreddit']
            subreddit.append(sub)
        except:
            sub = ''
            subreddit.append(sub)

        try:
            selftext.append(post['selftext'])
        except:
            selftext.append('')

        created_utc.append(post['created_utc'])
        num_comments.append(post['num_comments'])
        score.append(post['score'])
        title.append(post['title'])
        user.append(author)

    return created_utc, num_comments, score, subreddit, title, selftext, labels, user

def scrape_user_posts():
    print('scrape_user_posts()')
    troll_posts = {}
    created_utc = []
    num_comments = []
    score = []
    subreddit = []
    title = []
    selftext = []
    labels = []
    user = []
    counter = 0

    # print('scrape troll posts')
    # with open('bot_profiles.txt') as f:
    #     data = json.load(f)
    #     for author in data:
    #         counter+=1
    #         print(counter)
    #
    #         created_utc1, num_comments1, score1, subreddit1, title1, selftext1, labels1, user1 \
    #             = get_user_posts(author, is_bot=True)
    #
    #         if len(created_utc1) != 0:
    #             created_utc += created_utc1
    #             num_comments += num_comments1
    #             score += score1
    #             subreddit += subreddit1
    #             title += title1
    #             selftext += selftext1
    #             labels += labels1
    #             user += user1
    #
    # troll_posts['created_utc'] = created_utc
    # troll_posts['num_comments'] = num_comments
    # troll_posts['score'] = score
    # troll_posts['subreddit'] = subreddit
    # troll_posts['title'] = title
    # troll_posts['selftext'] = selftext
    # troll_posts['label'] = labels
    # troll_posts['user'] = user
    #
    # print('Write troll post data')
    # with open('data/troll_posts.txt', 'w') as f:
    #     json.dump(troll_posts, f)

    print('scrape normie posts')
    normie_posts = {}
    with open('normie_profiles.txt') as f:
        data = json.load(f)
        for author in data:
            counter += 1
            print(counter)
            if counter < 500:
                continue
            if counter == 900:
                break
            print(counter)
            created_utc1, num_comments1, score1, subreddit1, title1, selftext1, labels1, user1 \
                = get_user_posts(author, is_bot=False)

            if len(created_utc1) != 0:
                created_utc += created_utc1
                num_comments += num_comments1
                score += score1
                subreddit += subreddit1
                title += title1
                selftext += selftext1
                labels += labels1
                user += user1

    normie_posts['created_utc'] = created_utc
    normie_posts['num_comments'] = num_comments
    normie_posts['score'] = score
    normie_posts['subreddit'] = subreddit
    normie_posts['title'] = title
    normie_posts['selftext'] = selftext
    normie_posts['label'] = labels
    normie_posts['user'] = user

    print('Write normie post data')
    with open('data/normie_posts2.txt', 'w') as f:
        json.dump(normie_posts, f)

    return None

def get_comment_data_from_user(author, last_utc):
    url = 'https://api.pushshift.io/reddit/comment/search?after=' + last_utc + '&before=1523318400&size=500&author=' + author
    web_url = urllib.request.urlopen(url)
    contents = web_url.read()
    encoding = web_url.info().get_content_charset('utf-8')
    data = json.loads(contents.decode(encoding))
    return data

def get_user_comments(author, is_bot=True):
    print('get_user_comments()')
    last_utc = '1428624000'
    comments = []
    labels = []
    created_utc = []
    score = []
    subreddit = []
    user = []

    # Loop through all comments between 1428624000 (4/10/2015) to 1523318400 (4/10/18)
    # These are the dates that the bots were active
    print('Get comments from ' + author)

    # Add each comment to the user
    time.sleep(1)
    data = get_comment_data_from_user(author, last_utc)['data']
    for comment in data:

        if is_bot:
            labels.append(1)
        else:
            labels.append(0)

        try:
            sub = comment['subreddit']
            subreddit.append(sub)

        except:
            sub = ''
            subreddit.append(sub)

        comments.append(comment['body'])
        created_utc.append(comment['created_utc'])
        score.append(comment['score'])
        user.append(author)

    return comments, labels, created_utc, score, subreddit, user

def scrape_user_comments():
    print('scrape_user_comments()')
    troll_comments = {}
    normie_comments = {}
    text = []
    labels = []
    created_utc = []
    score = []
    subreddit = []
    user = []
    counter = 0

    # print('scrape bot comments')
    # with open('bot_profiles.txt') as f:
    #     data = json.load(f)
    #     for author in data:
    #         counter+=1
    #         print(counter)
    #         text1, labels1, created_utc1, score1, subreddit1, user1 = get_user_comments(author, is_bot=True)
    #
    #         if len(text1) != 0:
    #             text += text1
    #             labels += labels1
    #             created_utc += created_utc1
    #             score += score1
    #             subreddit += subreddit1
    #             user += user1
    #
    # troll_comments['comments'] = text
    # troll_comments['label'] = labels
    # troll_comments['created_utc'] = created_utc
    # troll_comments['score'] = score
    # troll_comments['subreddit'] = subreddit
    # troll_comments['user'] = user
    #
    # print('Write troll comment data')
    # with open('data/troll_comments.txt', 'w') as f:
    #     json.dump(troll_comments, f)

    text = []
    labels = []
    created_utc = []
    score = []
    subreddit = []
    user = []

    print('scrape normie comments')
    counter=0
    with open('normie_profiles.txt') as f:
        data = json.load(f)
        for author in data:
            if counter < 501:
                counter+=1
                continue
            text1, labels1, created_utc1, score1, subreddit1, user1 = get_user_comments(author, is_bot=False)

            print(counter)
            counter+=1
            if len(text1) != 0:
                text += text1
                labels += labels1
                created_utc += created_utc1
                score += score1
                subreddit += subreddit1
                user += user1

    normie_comments['comments'] = text
    normie_comments['label'] = labels
    normie_comments['created_utc'] = created_utc
    normie_comments['score'] = score
    normie_comments['subreddit'] = subreddit
    normie_comments['user'] = user

    print('Write normie comment data')
    with open('data/normie_comments2.txt', 'w') as f:
        json.dump(normie_comments, f)


def write_data(filename, data):
    with open(filename, 'a') as f:
        f.write(data)
        f.write('\n')

#scrape()
#scrape_user_comments()
scrape_user_posts()

