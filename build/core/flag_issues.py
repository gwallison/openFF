import pandas as pd
import os

class Disclosure_Issues():
    def __init__(self,df):
        self.df = df
        self.gb = df.groupby('DisclosureId',as_index=False)[['APINumber','TotalBaseWaterVolume','has_TBWV',
                                                             'is_duplicate','MI_inconsistent','ws_perc_total']].first()

    # ALL Issues must be named "dIssues_x"  where x is usually a consecutive number.
    # x will become the flag's name as in "d_x"
        
    def get_disc_set(self,cond):
        disc_set = self.gb[cond].DisclosureId.tolist()
        return disc_set

    def dIssue_001(self):
        '''TotalBaseWaterVolume is missing or zero. Mass calculations are not possible.'''
        cond = self.gb.has_TBWV==False
        return self.get_disc_set(cond)

    def dIssue_002(self):
        """ this disclosure has a duplicate in FracFocus; that is, has the same APINumber and JobEndDate."""
        cond = self.gb.is_duplicate
        return self.get_disc_set(cond)

    def dIssue_003(self):
        """ The MassIngredient data do not pass the internal consistency test, so are is used when reporting mass."""
        cond = self.gb.MI_inconsistent
        return self.get_disc_set(cond)

    def dIssue_004(self):
        """ The reported water source percentages do not sum to 100%"""
        cond = ~(self.gb.ws_perc_total==100)
        return self.get_disc_set(cond)

class Record_Issues():
    def __init__(self,df):
        self.df = df

    # ALL Issues must be named "rIssues_x"  where x is usually a consecutive number.
    # x will become the flag's name as in "r_x"

    def get_rec_set(self,cond):
        reckey_set = self.df[cond].reckey.tolist()
        return reckey_set

    def rIssue_001(self):
        """This flag indicates that a record is a redundant duplicate of another in the same disclosure."""
        c1 = self.df.dup_rec
        return self.get_rec_set(c1)

    def rIssue_002(self):
        """PercentHFJob is 0 or not reported; mass cannot be calculated and MassIngredient is typically also missing."""
        c1 = self.df.ingKeyPresent & ~(self.df.PercentHFJob>0)
        return self.get_rec_set(c1)

class Flag_issues():
    """Used to detect known data issues in the FracFocus data and generate appropriate flags to warn users.
    For each issue, a list is returned of DisclosureId (or IngredientsId) for the flags"""

    def __init__(self,df):
        self.df = df
        self.dIssues = Disclosure_Issues(df)
        self.rIssues = Record_Issues(df)
        self.get_disc_issues()
        self.get_rec_issues()

    def get_disc_issues(self):
        self.disc_issue_dic = {}
        for item in dir(self.dIssues):
            if item[:7] == 'dIssue_':
                name = 'd_'+item[7:]
                self.disc_issue_dic['self.dIssues.'+item+'()'] = name
        # print(self.disc_issue_dic)

    def make_disc_flag_df(self,disc_set,disc_issues):
        self.disc_df = pd.DataFrame({'DisclosureId':list(disc_set)})
        for issue in disc_issues:
            self.disc_df[issue[1]] = self.disc_df.DisclosureId.isin(issue[0])


    def get_rec_issues(self):
        self.rec_issue_dic = {}
        for item in dir(self.rIssues):
            if item[:7] == 'rIssue_':
                name = 'r_'+item[7:]
                self.rec_issue_dic['self.rIssues.'+item+'()'] = name
        # print(self.rec_issue_dic)

    def make_rec_flag_df(self,reckey_set,rec_issues):
        self.rec_df = pd.DataFrame({'reckey':list(reckey_set)})
        for issue in rec_issues:
            self.rec_df[issue[1]] = self.rec_df.reckey.isin(issue[0])

    def detect_all_issues(self):
        disc_set = set()
        names = []
        disissues = []
        for test in self.disc_issue_dic.keys():
            name = self.disc_issue_dic[test]
            lst = eval(test)
            # print(lst)
            print(f'generating flags for: {name}')
            disc_set.update(lst)
            names.append(name)
            disissues.append((lst,name))
        # make sure we don't have duplicate names
        seen = set()
        dupes = [x for x in names if x in seen or seen.add(x)]
        assert len(dupes)== 0, f'Duplicates in flag names: {dupes}'
        self.make_disc_flag_df(disc_set,disissues)

        rec_set = set()
        names = []
        recissues = []
        for test in self.rec_issue_dic.keys():
            name = self.rec_issue_dic[test]
            lst = eval(test)
            print(f'generating flags for: {name}')            
            rec_set.update(lst)
            names.append(name)
            recissues.append((lst,name))
        # make sure we don't have duplicate names
        seen = set()
        dupes = [x for x in names if x in seen or seen.add(x)]
        assert len(dupes)== 0, f'Duplicates in flag names: {dupes}'

        self.make_rec_flag_df(rec_set,recissues)

        # get the IDs into rec_df
        # self.rec_df = pd.merge(self.df[['DisclosureId','IngredientsId','reckey']],
        #                        self.rec_df,on='reckey',how='right',validate='1:1')

    