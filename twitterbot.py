# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 10:12:13 2019

@author: edoardottt

version = 1.3.3


This is the main file.
This file must be execute from the command line because It have to read the input arguments (via getopt).
It searches for tweet links found in your personal Feed/via search input field.
It can: Put likes on tweets and retweets them.
It defines a class called TwitterBot.
TwitterBot elements are built with 6 elements: username, password, likes ,retweets, keywords, followers.


This file is under MIT License.


"""


#VARIABLES TO CHANGE-----------------------------
email_email = '' # user's username
email_password = '' # user's password
password_flag = False   # True if the password has been entered
keywords = []   # the list of words you want to search in the input field
connection = 3  # time to wait the website load the content completely
keywords_flag = False    # True if the -k option has been entered
stat_flag = False   # True if the -s option has been entered
my_flag = False     # True if the -m option has been entered
info_flag = False   # True if the -i option has been entered
help_flag = False   # True if the -h option has been entered
limit = 50000   # Limit of the links crawled

#required libraries-----------------------------------------------
import time
import getopt
import socket
import getpass
import random
import datetime
import check_user
import add_result
import analyze_stat
import sys,usage

#write log into log file
def write_log(ex):
    f = open("twitterBot_log.txt",'a+')
    f.write('-----------'+str(datetime.datetime.now())+'----------\n')
    f.write(str(ex)+'\r\n')
    f.close()

try:
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
except Exception as ex:
    write_log(ex)
    usage.print_usage(3)

# options input  
try:
    options,remainder =getopt.getopt(sys.argv[1:], 'u:k:smih',['username','keywords','stat','mine','info','help'])  # all the options allowed
    for opt, arg in options:
        if opt in ('-u','--username'):
            email_email = arg
        elif opt in ('-k','--keywords'):
            try:
                keywords_flag = True
                keywords = arg.split(',')   # if more than one keyword have been entered, split them and put into keywords
            except Exception as ex:
                write_log(ex)
                usage.print_usage(0)
        elif opt in ('-s','--stat'):
            stat_flag = True
        elif opt in ('-m','--mine'):
            my_flag = True
        elif opt in ('-i','--info'):
            info_flag = True
        elif opt in ('-h','--help'):
            help_flag = True
except Exception as ex:
    write_log(ex)
    usage.print_usage(0)

#check internet connection status
def internet_check(host="8.8.8.8", port=53):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        write_log(ex)
        return False

# twitterBot class definition
class TwitterBot:
    
    def __init__(self, username, password,likes,retweets,keywords,followers):
        self.username = username
        self.password = password
        self.likes = 0
        self.retweets = 0
        self.followers = 0
        self.keywords = keywords
        self.links = []
        self.bot = webdriver.Firefox()
        
    def generate_random(self):  # It returns a random value between 5 and 8. That number indicates the seconds to be wait 
        rand = random.randint(5,8)
        return rand
    def generate_mid_random(self):  # Like a coin toss. 1/2 True - 1/2 False
        rand = random.randint(1,2)
        if(rand == 1):
            return True
        else:
            return False
    
    def close(self):
        self.bot.close()
    
    # login
    def login(self): 
        bot = self.bot
        bot.get('https://twitter.com/')     # Get the content of https://twitter.com/
        time.sleep(self.generate_random())  # This line of code WHEREVER wait for n [5-8] seconds.
        try:
            email = bot.find_element_by_class_name("email-input")       # Get the email input field.
            password = bot.find_element_by_name('session[password]')    # Get the password input field.
            email.clear()   # clear the email input field
            password.clear()    # clear the password input field
            email.send_keys(self.username)  # confirm
            password.send_keys(self.password)
            password.send_keys(Keys.RETURN) # send the inputs entered
            time.sleep(self.generate_random())  
            auth_flag = None
            try:
                auth_flag = bot.find_element_by_css_selector("h1.Icon.Icon--bird.bird-topbar-etched") # auth_flag = get the bird icon on top of the page if the authentication is Okay
            except Exception as ex:
                write_log(ex)
                usage.print_usage(1)
            if (auth_flag != None):     # if the user is authorized
                follower_elem = bot.find_element_by_css_selector('li.ProfileCardStats-stat:nth-child(3) > a:nth-child(1) > span:nth-child(2)')
                self.followers = follower_elem.get_attribute('data-count') # get the followers count
                #bot.find_element_by_css_selector('a.css-4rbku5:nth-child(7) > div:nth-child(1)').click()
                #follower_elem = bot.find_element_by_css_selector('div.r-18u37iz:nth-child(5) > div:nth-child(2) > a:nth-child(1) > span:nth-child(1) > span:nth-child(1)')
                #self.followers = follower_elem.text # get the followers count
                #bot.find_element_by_css_selector('a.r-1habvwh:nth-child(1) > div:nth-child(1)').click()
                return True
        except Exception as ex:
            write_log(ex)
            usage.print_usage(2)
    
    # add tweets links from search input field by typing the hashtags entered
    def add_links(self):
        print('Collecting links...')
        bot = self.bot
        for keyword in self.keywords:
            bot.get('https://twitter.com/search?q=' + keyword + '&src=typd')    # search the i-th hashtag
            time.sleep(connection)
            bot.execute_script('window.scroll(0,document.body.scrollHeight)')   # scroll the page
            time.sleep(connection)
            tweets = bot.find_elements_by_class_name('tweet') # handle all the tweets shown
            self.links += [elem.get_attribute('data-permalink-path') for elem in tweets]    #get all the links of the tweets
        random.shuffle(self.links)
        print(str(len(self.links))+' links added!')
        
    #add tweets links from the personal feed    
    def add_links_my_home(self):
        print('Collecting links...')
        bot = self.bot
        for i in range(7):
            bot.execute_script('window.scroll(0,document.body.scrollHeight)')   #scroll the page
            time.sleep(connection)
        time.sleep(connection)
        tweets = bot.find_elements_by_class_name('tweet')   # handle all the tweets shown
        self.links = [elem.get_attribute('data-permalink-path') for elem in tweets]    #get all the links of the tweets
        random.shuffle(self.links)
        print(str(len(self.links))+' links added!')

    # put likes and maybe rwtweets all the tweets reached
    def crawl(self):
        print('TwitterBot started at '+str(datetime.datetime.now())[:-7]+" !")
        for link in self.links:
            if((not link is None) and (self.likes<limit)):  # if the tweets reached don't overcome the limit
                self.bot.get('https://twitter.com'+link)    # get the tweet page
                time.sleep(connection)
                try:
                    self.bot.find_element_by_class_name('HeartAnimation').click()   # like
                    self.likes += 1
                    time.sleep(1)
                    if(self.generate_mid_random()): # True probability = 0.5
                        # retweet the tweet
                        self.bot.find_element_by_css_selector("button.ProfileTweet-actionButton.js-actionButton.js-actionRetweet").click()
                        time.sleep(2)
                        # confirm the retweet
                        self.bot.find_element_by_class_name('RetweetDialog-retweetActionLabel').click()
                        self.retweets += 1
                    # print the info 
                    result = " | likes: " + str(self.likes)+' | '+"retweets: " + str(self.retweets)
                    print(str(datetime.datetime.now())[:-7] + result,end='\r')
                    time.sleep(self.generate_random())
                except Exception as ex:
                    time.sleep(15)
        print('')
        print('Finished!')


# if -u and ( -m OR -k)
if((email_email!='')and(not stat_flag)and((my_flag and (not keywords_flag))or(keywords_flag and (not my_flag)))):
    
    email_password = getpass.getpass('Insert password for ' +email_email +':') # password input via getpass
    edoBot = TwitterBot(email_email,email_password,0,0,keywords,0) #create the bot
    network_status = internet_check()
    if (not network_status):
        usage.print_usage(6) # if the network connection isn't active
    authenticated = edoBot.login()  # login
    if(authenticated): 
        if(check_user.check_if_user_exists(edoBot.username,edoBot.password)):
            print('Welcome back, ' + edoBot.username + ' !')
        else:
            print('Logged in as '+edoBot.username+' !')
        if(keywords_flag and(not my_flag)):
            edoBot.add_links()
        elif(my_flag and(not keywords_flag)):
            edoBot.add_links_my_home()
        else:
            usage.print_usage(8)
        edoBot.crawl() #here start the bot
        edoBot.close()
        timee = datetime.datetime.now()
        add_result.add_stat(edoBot.username,timee,edoBot.likes,edoBot.retweets,edoBot.followers)
        
# if -u and -s 
elif((email_email!='')and(not keywords_flag)and stat_flag and(not my_flag) and(not info_flag) and(not help_flag)):
    email_password = getpass.getpass('Insert password for ' +email_email +':') # password input via getpass
    analyze_stat.check_stat(email_email,email_password)
    
# if -i
elif((email_email=='') and(not stat_flag)and(not my_flag)and(not keywords_flag)and(not help_flag)and(info_flag)):
    usage.print_usage(7)
    
# if -h
elif((email_email=='') and(not stat_flag)and(not my_flag)and(not keywords_flag)and help_flag and(not info_flag)):
    usage.print_usage(0)
else:
    usage.print_usage(8)