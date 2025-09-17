import pandas as pd
from datetime import datetime
import sys
import os
import glob
import re
from functools import reduce
from pandasgui import show


class EQInventoryMonitor:
    def __init__(self, install_directory):
        self.install_dir = install_directory
        self.items_df = self.get_inventory_file_data()
        self.characters_modified_df = self.items_df[['Character', 'UpdatedAt']].drop_duplicates(inplace=True)
        self.character_list = list(self.items_df['Character'])

    def get_inventory_file_data(self) -> pd.DataFrame:
        inventory_files = glob.glob("*-Inventory.txt", root_dir=self.install_dir)
        result_list = []

        for file_name in inventory_files:
            file_path = os.path.join(self.install_dir, file_name)
            modified_epoch = os.path.getmtime(file_path)
            modified_ts = datetime.fromtimestamp(modified_epoch)
            
            char_name = re.match(r".+?-", file_name).group(0).replace("-", "")
            
            df = pd.read_csv(file_path, sep='\t')
            df.insert(0, 'Character', char_name)
            df['UpdatedAt'] = modified_ts
            df['Character'] = df['Location'].apply(lambda c: 'SHARED-BANK' if str(c).startswith('SharedBank') else char_name)
            result_list.append(df)
            
        final_df = reduce(lambda x,y: pd.concat([x,y], axis=0), result_list)
        final_df = final_df.loc[final_df['Name'] != 'Empty']
        print(len(final_df.index))
        unique_cols = list(final_df.columns).remove('UpdatedAt')
        final_df.drop_duplicates(subset=unique_cols, inplace=True)
        print(len(final_df.index))
        return final_df


if __name__ == '__main__':
    #install_dir = input("Enter THJ installation path: ")
    install_dir = r"C:\THJ"
        
    inventory = EQInventoryMonitor(install_dir)
    
    
    show(inventory.items_df)
