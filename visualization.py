import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

class visualization:

    def __init__(self, data):
        self.data = data

    # View active sessions per week
    def active_sessions(self):

        # Aggregate the sessions in a weekly manner (7 days aggregate)
        active_users = self.data.resample('W-Mon', on='login_date').size().reset_index()
        active_users.columns = ['Date', 'Active_Sessions']
        active_users['Date'] = active_users['Date'].dt.date  # Select only the day of the date for plotting
        active_users.plot('Date', 'Active_Sessions', kind='bar')
        plt.title("Active Sessions per week")
        plt.ylabel("Number of Sessions")
        plt.xticks(rotation=45)

        # Similar process as above but this time exclude sessions where inactive_duration is greater than the session
        active_users_exc = self.data[self.data['inactive_duration'] < self.data['session_duration']]

        active_users_exc = active_users_exc.resample('W-Mon', on='login_date').size().reset_index()
        active_users_exc.columns = ['Date', 'Active_Sessions']
        active_users_exc['Date'] = active_users_exc['Date'].dt.date

        active_users_exc.plot('Date', 'Active_Sessions', kind='bar')
        plt.title("Active Sessions excluding incorrect data per week")
        plt.ylabel("Number of Sessions")
        plt.xticks(rotation=45)

    # View the breakdown of new/unique users and returning users in overall weekly sessions
    def unique_vs_returning_users(self):

        users_list = []  # Maintain an user list to check if an user already had a session
        # Flags list to keep track of new/unique and returning users
        new_users = []
        returning_users = []

        for i, j in self.data.iterrows():
            if j['customer_id'] not in users_list:  # check if the user is a new user or not and set the flags accordingly
                new_users.append(1)
                returning_users.append(0)
                users_list.append(j['customer_id'])
            else:
                new_users.append(0)
                returning_users.append(1)

        # Add the flags list as additional columns in the original dataframe
        df_u = self.data.assign(unique_users=new_users, returning_users=returning_users)

        users_bd = df_u[['login_date', 'unique_users', 'returning_users']]
        # Aggregate the sessions in a weekly manner (7 days aggregate)
        users_bd = users_bd.resample('W-Mon', on='login_date').sum().reset_index()

        users_bd['login_date'] = users_bd['login_date'].dt.date
        users_bd = users_bd.set_index(['login_date'])  # set "login_date" as index for the plotting purpose

        users_bd[["unique_users", "returning_users"]].plot(kind="bar", stacked=True)
        plt.xticks(rotation=45)
        plt.title(" New Users VS Returning Users Breakdown ")
        plt.xlabel("Date")
        plt.ylabel("Number of Sessions")


    # View the user engagement attributes such as 'Likes','Projects' and "Comments"
    def events_engagement(self):

        events = self.data[['login_date', 'session_projects_added', 'session_likes_given', 'session_comments_given']]
        # Aggregate the sessions in a weekly manner (7 days aggregate)
        events = events.resample('W-Mon', on='login_date').sum().reset_index()

        plt.rcParams['figure.figsize'] = [12, 8]
        plt.plot(events.login_date, events.session_likes_given, label='Likes', marker='o')
        plt.plot(events.login_date, events.session_projects_added, label='Projects', marker='o')
        plt.plot(events.login_date, events.session_comments_given, label='Comments', marker='o')
        # plt.ylim(0,30)
        plt.grid(which='major', axis='both', linestyle='-.', linewidth=0.75)
        plt.xticks(rotation=60, fontsize=14)
        plt.yticks(fontsize=14)
        plt.legend(fontsize=14)
        plt.xlabel("Date")
        plt.ylabel("Events Count")
        plt.title('Events Engagement', fontsize=20)

    # Calculate the percentage variation in the events engagament from the previous week
    def percent_variation(self):

        events = self.data[['login_date', 'session_projects_added', 'session_likes_given', 'session_comments_given']]
        events = events.resample('W-Mon', on='login_date').sum().reset_index()

        events = events.loc[:, events.columns != 'login_date']  # Unselect date column
        events = events.pct_change()  # calculate percentage variation

        events.insert(loc=0, column='date', value=self.data['login_date'])  # Insert back the "login_date" column

        events['date'] = events['date'].dt.date
        events = events[0:-1]  # unselect the last record as the last week has only 2 days(oct-29 & 30)
        return (events)

    # View the percentage variation in events engagement
    def events_engagement_percentage_variation(self):

        events = self.percent_variation()  # returns a dataframe with percentage variation in the events
        pos = list(range(len(events['session_projects_added'])))
        width = 0.25

        fig, ax = plt.subplots(figsize=(10, 5))

        plt.bar(pos,

                events['session_projects_added'],

                width,

                alpha=0.5,

                color='#EE3224',

                label=events['date'].iloc[0])

        plt.bar([p + width for p in pos],

                events['session_likes_given'],

                width,

                alpha=0.5,

                color='#F78F1E',

                label=events['date'][1])

        plt.bar([p + width * 2 for p in pos],

                events['session_comments_given'],

                width,

                alpha=0.5,

                color='#FFC222',

                label=events['date'][2])

        ax.set_ylabel('Percentage Variation')
        ax.set_xlabel('Week')

        ax.set_title('Event Engagement')

        ax.set_xticks([p + 1.5 * width for p in pos])

        ax.set_xticklabels(events['date'])
        plt.xticks(rotation=45)
        vals = ax.get_yticks()
        ax.set_yticklabels(['{:,.2%}'.format(x) for x in vals])
        plt.xlim(min(pos) - width, max(pos) + width * 4)


        plt.legend(['Projects', 'Likes', 'Comments'], bbox_to_anchor=(1.05, 1.0), loc='upper left')
        plt.tight_layout()
        plt.grid(True)
        plt.show()

    # Attempt to find the source of bugs
    def source_of_bugs(self):

        events = self.percent_variation()  # returns a dataframe with percentage variation in the events

        bugs = self.data[['login_date', 'bugs_in_session']]
        bugs = bugs.resample('W-Mon', on='login_date').sum().reset_index()
        bugs = bugs[0:-1]  # Unselect the last week record

        # Create combo chart
        fig, ax1 = plt.subplots(figsize=(10, 6))
        color = 'tab:green'
        # bar plot creation
        ax1.set_title('Bugs VS Comments Percentage Variation', fontsize=16)
        ax1.set_xlabel('Week', fontsize=16)

        ax1 = sns.barplot(x=events.index + 1, y=events.session_comments_given, data=events, palette='summer')
        ax1.set_ylabel('Comments Variation in Percentage', fontsize=16)
        ax1.tick_params(axis='y')
        # specify we want to share the same x-axis
        ax2 = ax1.twinx()
        color = 'tab:red'
        # line plot creation
        ax2.set_ylabel('Avg Percipitation %', fontsize=16)
        ax2 = sns.lineplot(x=bugs.index, y='bugs_in_session', data=bugs, sort=False, color=color)
        ax2.set_ylabel("Number of Bugs")
        ax2.tick_params(axis='y', color=color)
        # show plot
        plt.show()

    # View the average session duration per day
    def average_session_duration(self):

        avg_session = self.data[['login_date', 'session_duration']]
        avg_session = avg_session.groupby(['login_date']).mean().reset_index()  # Calculate average session duration
        avg_session['session_duration'] = avg_session['session_duration'] / 60  # Convert seconds to minutes

        # avg_session.plot('login_date','session_duration')
        plt.plot(avg_session['login_date'].dt.day, avg_session['session_duration'])
        plt.xticks(np.arange(0, 30, 7))
        plt.grid(which='major', axis='x', linestyle='-.', linewidth=0.75, color='black')
        plt.xlabel("Days")
        plt.ylabel("Average Session time in minutes")
        plt.title("Average Session Duration per Day")