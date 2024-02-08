import os
import shutil
import traceback
import pandas as pd
from git import Repo  # pip install gitpython
import numpy as np

class GitHubGPTsSearchScraper:
    '''
    This scraper works a little differently than the others. It clones a repo from github with csvs of data. This
    '''
    args = None
    driver = None
    ID = "github_gpts_searchscraper"
    skip = True

    relevant_github_repo = "https://github.com/casssapir/gpt-list.git"
    repo_dir = "gpt-data"

    def clone_repo(self):
        # clone the repository url
        print("Cloning data...")
        if os.path.exists(self.repo_dir):
            self.cleanup_scrape()

        data_repo = Repo.clone_from(self.relevant_github_repo, self.repo_dir)
        return data_repo.working_tree_dir

    def extract_and_read_csvs(self, repo_dir):
        # Get all CSV files in the working dir_
        csvs = []
        # Iterate directory
        for file in os.listdir(repo_dir):
            # check only text files
            if file.endswith('.csv'):
                csvs.append(file)

        openai_ids = []
        for csv in csvs:
            # iteratively try finding the gpt_id column
            for i in range(0, 20):
                try:
                    csv_columns = pd.read_csv(os.getcwd() + "/gpt-data" + "/{}".format(csv),
                                              skiprows=i)
                    if "gpt_id" in csv_columns.columns.values:
                        openai_ids.append(csv_columns)
                        break
                except:
                    print(traceback.format_exc())
        ids = []
        for df in openai_ids:
            ids.append(df["gpt_id"].values)

        openai_id_shortcodes = list(set(np.concatenate(ids)))

        return openai_id_shortcodes

    def rm_r(self, path):
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        elif os.path.exists(path):
            os.remove(path)

    def cleanup_scrape(self):
        # since this touches the disk, we want to remove the repo once we've generated data
        print("Cleaning")
        self.rm_r(self.repo_dir)
        pass

    def scrape(self, email_reporting=False) -> list:
        if not self.skip:
            repo_path = self.clone_repo()
        else:
            repo_path = "/Users/evinjaff/github/gptsdatamining/gpt-data"
        shortcodes = self.extract_and_read_csvs(repo_path)
        # append https://chat.openai.com/g/g- to all strings in shortcodes

        return ["https://chat.openai.com/g/g-" + s + "-" for s in shortcodes]
