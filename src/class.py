from cleaning import *
from format import *
from feature_scaling import *
from feature_selection import *


class operation:
    def __init__(self, df, cleaning):
        self.df = df
        self.clean = cleaning
        self.clean_df = None
        self.formatted_df = None
        self.balanced_df = None

        self.cleaning_func()
        self.formatting_func()
        self.balancing_func()

    def cleaning_func(self):
        if self.clean:
            self.clean_df = clean_data(self.df)
        else:
            pass

    def formatting_func(self):
        if self.clean:
            self.formatted_df = format_data(self.clean_df)
        else:
            self.formatted_df = format_data(self.df)

    def balancing_func(self):
        self.balanced_df = balance_data(self.formatted_df)

    def final_data(self):
        result_df = self.formatted_df
        return result_df