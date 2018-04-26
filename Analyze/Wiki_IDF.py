import json
import os
import os.path
import hashlib
import string
import math
import re
import sys
import pickle

Encoding = 'utf-8'
OutputFileFolder = 'G:/wiki/idf/'
OutputFilePath = os.getcwd()+'/../'+'Analyze/output/idf.txt'
PicklePath = OutputFileFolder+'idf.pkl'


class CalculatedGlobalIDF:
    NumberOfDocs = 0
    Words = dict()

    def __init__(self, reload):
        if reload:
            CalculatedGlobalIDF.pickle_load()

    @staticmethod
    def append_doc(doc):
        CalculatedGlobalIDF.NumberOfDocs += 1
        for idx, word in enumerate(doc.words):
            if word in CalculatedGlobalIDF.Words:
                CalculatedGlobalIDF.Words[word] += 1
            else:
                CalculatedGlobalIDF.Words[word] = 1

    @staticmethod
    def calculate_idf():
        if not os.path.exists(OutputFileFolder):
            os.makedirs(OutputFileFolder)

        with open(OutputFilePath, "w", encoding=Encoding) as f:
            total_docs = '{"NumberOfDocs":%d}' % CalculatedGlobalIDF.NumberOfDocs
            f.write("%s\n" % total_docs)
            for word, count in CalculatedGlobalIDF.Words.items():
                idf_string = '{"%s":{"count":%d, "idf":%.6f}}' \
                             % (word, count, math.log(CalculatedGlobalIDF.NumberOfDocs/count))
                f.write("%s\n" % idf_string)

    @staticmethod
    def pickle_dump():
        with open(PicklePath, 'wb') as output_data:
            pickle.dump(CalculatedGlobalIDF.NumberOfDocs, output_data, pickle.HIGHEST_PROTOCOL)
            pickle.dump(CalculatedGlobalIDF.Words, output_data, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def pickle_load():
        with open(PicklePath, 'rb') as input_data:
            CalculatedGlobalIDF.NumberOfDocs = pickle.load(input_data)
            CalculatedGlobalIDF.Words = pickle.load(input_data)


class Doc:
    Check_digital_pattern = re.compile("^.*[0-9]+.*$")
    Check_punctuation_pattern = re.compile("^.*[\<\>\"\(\)/\\\"=,:;\*\!\%\^\&\[\]\{\}\-\_\+\?]+.*$")

    def __init__(self, doc_id, file_path, json_data):
        self.doc_id = doc_id
        self.file_path = file_path
        self.words = set()

        self.__process_text__(json_data)

    def __process_text__(self, json_data):
        text = str(json_data['text'])
        for idx, word in enumerate(text.split()):
            word = word.strip(string.punctuation).lower()
            if len(word) > 0 \
                    and word not in self.words \
                    and not Doc.Check_digital_pattern.match(word) \
                    and not Doc.Check_punctuation_pattern.match(word):
                self.words.add(word)


def read_json_data_from_file():
    base_file_path = 'G:/wiki/extracted/'

    for char_a in string.ascii_uppercase:
        for char_b in string.ascii_uppercase:
            for file_idx in range(100):
                file_path = ''.join([base_file_path, char_a, char_b, '/', 'wiki_', str(file_idx).zfill(2)])
                if os.path.exists(file_path):
                    with open(file_path, encoding=Encoding) as fh:
                        for idx, line in enumerate(fh):
                            data = json.loads(line)
                            md5_str = hashlib.md5(line.encode(Encoding)).hexdigest()
                            doc_id = ''.join([char_a, char_b, "_", str(file_idx).zfill(2),
                                              "_", str(idx).zfill(4), "_", md5_str])
                            doc = Doc(doc_id, file_path, data)
                            CalculatedGlobalIDF.append_doc(doc)
                else:
                    break

                print(file_path)
            #return


def main(argv):
    #CalculatedGlobalIDF.pickle_load()
    read_json_data_from_file()
    CalculatedGlobalIDF.calculate_idf()
    pass


if __name__ == "__main__":
    main(sys.argv)



