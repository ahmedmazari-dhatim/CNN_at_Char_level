from abbyextractor import AbbyExtractor
import re
import pandas as pd
import Levenshtein as lev
import pprint
from fuzzyfonction import FuzzyFct
import fuzzy_string_matching as fuzzyStr
from nltk.corpus import stopwords
from word import WordFeature

pp = pprint.PrettyPrinter(indent=4)

class AbbyTraining:
    pattern_price = re.compile(r"^-?\d+[,.]?\d*$")
    pattern_price_2 = re.compile(r"(\d[\d\s]+)$")
    pattern_price_3 = re.compile(r"^\d+[.]\d+[,]\d*-?$")
    pattern_date = re.compile(r"(\d{2})(\/|.)(\d{2})(\/|.)(\d{2,4})")
    seuil_jaro = 0.90
    seuil_lev = 3
    seuil_word_improved_jaro = 0.8+0.9 # sup to 80 with jaro without improvement and 90 with improvement
    col_prices = ["montant_total_ht", "montant_total_ttc", "montant_total_tva", "acompte", 'remise',
                  "net_a_payer",
                  "quantite", "pu", "montant_tva_ligne", "montant_ht_ligne", "remise_ligne", "montant_ttc_ligne"]
    col_dates = ["date_facture", "date_prestation"]

    def __init__(self, filexml):
        abbbyextractor = AbbyExtractor(filexml)
        self.ens_brut_blcks = abbbyextractor.get_words()
        #self.ens_brut_blcks= WordFeature.get_representation()

        # df = pd.read_csv(filecsv, sep=";")
        #df = df.rename(columns={df.columns[0]:'nom_fichier'})

        #self.numen_data = df[df.nom_fichier == filename+".pdf"]
        # self.numen_data = self.numen_data.drop('nom_fichier', 1)

        #for col in self.col_prices:
        #    if pd.notnull(self.numen_data[col]).sum() != 0:
        #        self.numen_data[col] = self.numen_data[col].fillna(0)

        # for i, row in self.numen_data.remise_ligne.str.contains('%').iteritems():
        #   if row == True or row == False:
        #        if '%' not in self.numen_data.remise_ligne.loc[i]:
        #            remise = float(self.numen_data.remise_ligne.loc[i].replace(',', '.'))
        #            self.numen_data.loc[i, 'remise_ligne'] = round(remise*100, 2)


        #pp.pprint(self.numen_data)

       # self.categorize()
        self._flatten()
        #self._clean_post_categorisation()

        pp.pprint(self.words_list)

        #for i, block in enumerate(self.ens_brut_blcks):
        #    print(i, block)

    def categorize(self):

        for category, data in self.numen_data.iteritems():
            for words_looking_for in data:
                words_looking_for = str(words_looking_for)
                if words_looking_for == 'nan':
                    continue

                lines = words_looking_for.split('\n')
                for line in lines :
                    words_looking_for = line.split(' ')

                    for i, block in enumerate(self.ens_brut_blcks):
                        self.categorize_text_block(i, category, words_looking_for)

    def categorize_text_block(self, block_i, category, words_looking_for):
        block = self.ens_brut_blcks[block_i]
        block_string = self._get_block_string(block)
        for j, line in enumerate(block):
            line_string = self._get_line_string(line)
            for k, word in enumerate(line):
                if category in self.col_prices:
                    if self._if_price(word.string, words_looking_for, line_string):
                        self.ens_brut_blcks[block_i][j][k].add_category(category)


                elif category in self.col_dates:
                    if self._if_date(word.string, words_looking_for):
                        self.ens_brut_blcks[block_i][j][k].add_category(category)


                else:
                    if self._if_text(word.string, words_looking_for, block_string, line_string):
                        self.ens_brut_blcks[block_i][j][k].add_category(category)


    def _if_price(self, currentword, words_looking_for, line_string):
        if self.pattern_price.match(currentword) is not None:
            for w in words_looking_for:
                w = w.replace('%','')
                w = w.replace(',', '.')
                if self.pattern_price.match(w) is not None:

                    if lev.distance(currentword.replace(',','.'), w) < self.seuil_lev and lev.jaro_winkler(currentword.replace(',','.'), w) > self.seuil_jaro:
                        return True

                    if self.pattern_price_2.search(line_string):
                        match = "".join(self.pattern_price_2.search(line_string).group(0).split(" "))
                        if lev.distance(match, w) < self.seuil_lev and lev.jaro_winkler(match, w) > self.seuil_jaro:
                            return True
                    try :
                        price = float(currentword.replace(',','.'))
                        price_looking_for =  abs(float(w))
                        if price == price_looking_for or round(price,2) == round(price_looking_for,2):
                            return True
                    except ValueError:
                        pass

        if self.pattern_price_3.match(currentword):
            currentword_cpy = currentword.replace(".", "")
            currentword_cpy = currentword_cpy.replace(",",".")
            currentword_cpy = currentword_cpy.replace("-", "")

            for w in words_looking_for:
                if self.pattern_price.match(w) is not None or self.pattern_price_3.match(w) is not None:
                    w = abs(float(w.replace(',','.')))

                    if float(currentword_cpy) == w:
                        return True
        return False

    def _if_date(self, currentword, words_looking_for):
        words_looking_for = words_looking_for[0].split('-')
        if self.pattern_date.match(currentword):
            match_obj = self.pattern_date.match(currentword)
            for w in words_looking_for:
                match_obj_2 = self.pattern_date.match(w)
                same_day = match_obj.group(1) == match_obj_2.group(1)
                same_month = match_obj.group(3) == match_obj_2.group(3)
                if same_day and same_month:
                    return True

        return False

    def _if_text(self, currentword, words_looking_for, block_string, line_string):
        phrase_looking_for = " ".join(words_looking_for)
        testword = True if True in [fuzzyStr.fuzzy_match(w, currentword) for w in words_looking_for] else False
        testblock = fuzzyStr.fuzzy_match(phrase_looking_for, block_string)
        testline = fuzzyStr.fuzzy_match(phrase_looking_for, line_string)

        french_stopwords = set(stopwords.words('french'))
        french_stopwords.add('no.')

        if testword +testblock +testline > 1:
            return True
        elif testword and currentword.lower() not in french_stopwords and len(currentword)==2:
            return True
        else:
            return False

    def _get_line_string(self, line):
        return " ".join([w.string for w in line])

    def _get_block_string(self, block):
        return " ".join([self._get_line_string(line) for line in block])

    def _flatten(self):
        self.words_list = list()
        for block in self.ens_brut_blcks:
            for line in block:
                    self.words_list.extend(line.copy())

    def _clean_post_categorisation(self):
        # regle 1, apres le dernier "netapayer" il ne peut y avoir aucune category provenant d'un tableau
        end_table = self._clean_footer()

        # regle 2, avant le premier "libelle", il ne peut y avoir de category ne provenant d'un tableau (except objet_facture)
        start_table = self._clean_header()

        print("start_table",start_table, "end_table", end_table)
        self._clean_table(start_table, end_table)



    def _clean_footer(self):
        table_category = ["montant_total_ht", "montant_total_ttc", "montant_total_tva", "acompte", "remise",
                          "net_a_payer",
                          "quantite", "pu", "montant_tva_ligne", "montant_ht_ligne", "remise_ligne",
                          "montant_ttc_ligne", "libelle", "objet_facture"]

        i = len(self.words_list) - 1
        while not self.words_list[i].contains_category("net_a_payer"):
            if list(filter(lambda x: x in table_category, self.words_list[i].category)):
               self.words_list[i].clean_category()
            i -= 1
            if i < 0: break

        return i

    def _clean_header(self):
        table_category = ["montant_total_ht", "montant_total_ttc", "montant_total_tva", "acompte", "remise",
                          "net_a_payer",
                          "quantite", "pu", "montant_tva_ligne", "montant_ht_ligne", "remise_ligne",
                          "montant_ttc_ligne", "libelle"]

        i = 0
        while not (self.words_list[i].contains_category("libelle")):
            if list(filter(lambda x: x in table_category, self.words_list[i].category)):
                self.words_list[i].clean_category()
            i+=1
            if i >= len(self.words_list): break

        return i

    def _clean_table(self, start_table, end_table):
        # Rule 1 : There is an unique net_a_payer
        self._unique_net_a_payer(end_table)
        self._remove_non_desired_cat_in_table(start_table, end_table)
        self._unique_totaux(start_table, end_table)
        self._remove_confusion_between_libelle_price(start_table, end_table)
        end_detail = self._find_end_detail_table(start_table, end_table)

        self._define_row_in_detail_table(start_table, end_detail)
        how_many_col = self._define_col_in_detail_table(start_table, end_detail)

        self._unique_pu_ht_ligne(how_many_col, start_table, end_detail)
        if end_detail != start_table:
            self._remove_weirdo_between_table_and_totals(end_detail, end_table)
            self._remove_weirdo_totals(end_detail,end_table)


    def _unique_net_a_payer(self, end_table):
        self.words_list[end_table].clean_category()
        self.words_list[end_table].add_category("net_a_payer")

    def _remove_non_desired_cat_in_table(self, start_table, end_table):
        to_remove = ["date_prestation", "date_facture", "fournisseur", "num_facture", "num_cmd_bytel", "net_a_payer"]

        for words in self.words_list[start_table:end_table]:
            intersection = list(filter(lambda x: x in to_remove, words.category))
            if intersection:
                for cat in intersection:
                    words.remove_category(cat)

    def _unique_totaux(self, start_table, end_table):
        i = end_table - 1
        flag_total_VAT_amount = False
        flag_total_HT_amount = False
        while (not flag_total_HT_amount or not flag_total_VAT_amount):
            if self.words_list[i].contains_category('montant_total_tva'):
                self.words_list[i].clean_category()
                self.words_list[i].add_category('montant_total_tva')
                flag_total_VAT_amount = True
            if self.words_list[i].contains_category('montant_total_ht') or self.words_list[i].contains_category(
                    'montant_total_ttc'):
                if flag_total_VAT_amount:
                    self.words_list[i].clean_category()
                    self.words_list[i].add_category('montant_total_ht')
                    flag_total_HT_amount = True
                else:
                    self.words_list[i].clean_category()
                    self.words_list[i].add_category('montant_total_ttc')
            i -= 1

        if flag_total_VAT_amount and flag_total_HT_amount:
            to_remove = ["montant_total_ttc", "montant_total_tva"]
            for words in self.words_list[start_table:i]:
                intersection = list(filter(lambda x: x in to_remove, words.category))
                if intersection:
                    for cat in intersection:
                        words.remove_category(cat)

    def _remove_confusion_between_libelle_price(self, start_table, end_table):
        for word in self.words_list[start_table:end_table]:
            flag = False
            for cat in self.col_prices:
                if word.contains_category(cat): flag = True
            if word.contains_category("libelle") and flag:
                word.remove_category("libelle")
            elif word.contains_category("libelle") and not flag:
                word.clean_category()
                word.add_category("libelle")

    def _find_end_detail_table(self, start_table, end_table):
        i = end_table-1
        flag = True
        while flag:
            if self.words_list[i].contains_category('montant_ht_ligne'):
                flag = False
            else:
                i -= 1

            if i < start_table: flag = False

        return i+1


    def _define_row_in_detail_table(self, start_table, end_detail):
        find_first_word_line = False
        fuzzyfct = None
        plus_moins = 30

        for indice_line in range(0, max(20,len(self.numen_data.index))):
            for w in self.words_list[start_table:end_detail]:
                if w.row is None and not find_first_word_line and w.contains_category("libelle"):
                    find_first_word_line = True
                    w.add_row(indice_line)
                    w.proba_row = 1

                    # Define new fuzzy logic function
                    word_size = w.b - w.t
                    center = w.t+int(word_size/2)

                    fuzz_definition = [center-plus_moins,
                                       w.t,
                                       w.b,
                                       center+plus_moins]
                    fuzzyfct = FuzzyFct(fuzz_definition)

                elif find_first_word_line:
                    proba = max(fuzzyfct.get_proba(w.t), fuzzyfct.get_proba(w.b))

                    if proba != 0:
                        w.change_if_best(indice_line, proba)

            find_first_word_line = False

    def _define_col_in_detail_table(self, start_table, end_detail):
        find_price = False
        fuzzyfct = None
        plus_moins = 150

        how_many_col = 0
        for indice_col in range(0, 3):
            for w in self.words_list[start_table:end_detail]:
                if w.col is None and not find_price and (w.contains_category('montant_ht_ligne') or w.contains_category('pu') or w.contains_category('montant_ttc_ligne')):

                    find_price = True
                    w.add_col(indice_col)
                    w.proba_col = 1

                    # Define new fuzzy logic function
                    word_size = w.r - w.l
                    center = w.r+int(word_size/2)

                    fuzz_definition = [center-plus_moins,
                                       w.l,
                                       w.r,
                                       center+plus_moins]
                    fuzzyfct = FuzzyFct(fuzz_definition)
                    how_many_col += 1
                elif find_price and (w.contains_category('montant_ht_ligne') or w.contains_category('pu') or w.contains_category('montant_ttc_ligne')):
                    proba = max(fuzzyfct.get_proba(w.l), fuzzyfct.get_proba(w.r))

                    if proba != 0:
                        w.change_if_best(indice_col, proba, "col")

            find_price = False

        return how_many_col


    def _unique_pu_ht_ligne(self, how_many_col, start_table, end_detail):
        order = ["pu", "montant_ht_ligne", "montant_ttc_ligne"]

        for w in self.words_list[start_table:end_detail]:
            if w.col is not None :
                w.clean_category()
                w.add_category(order[w.col])


    def _remove_weirdo_between_table_and_totals(self, end_detail, end_table):
        for w in self.words_list[end_detail+1:end_table]:
            if w.contains_category('montant_total_ht'):
                break
            elif w.contains_category('code_tva_ligne'):
                continue
            else:
                w.clean_category()

    def _remove_weirdo_totals(self, end_detail, end_table):
        flag = False
        for w in self.words_list[end_detail+1:end_table]:
            if w.contains_category('montant_total_ht'):
                flag = True
            elif flag == True and \
                    not (w.contains_category('montant_total_ht') or\
                        w.contains_category('montant_total_ttc') or\
                        w.contains_category('montant_total_tva') or \
                        w.contains_category('code')):
                w.clean_category()