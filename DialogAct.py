import sys
from math import log, ceil
from collections import defaultdict, Counter
from sklearn.metrics import accuracy_score
import re

class DialogAct(object):

    def __init__(self):
        self.all_train_samples = 0
    def train(self, filename):
        self.prior_count = Counter()
        self.prior_probability = {}

        self.tag_adv_word_count = {}
        self.tag_stu_word_count = {}

        self.answers = []

        self.word_count_for_each_tag = {}
        self.V = 0

        with open(filename, 'r') as f:
            last_tag = ""
            #advisor_asking = False
            for line in f.readlines():
                line = line.lower().strip()
                person = line.split(":")[0]
                if person == "advisor":
                    tag = re.search(r"\[([A-Za-z0-9_-]+)\]", line).group(1)
                    last_tag = tag
                    self.prior_count[tag] += 1
                    self.all_train_samples += 1
                    if tag not in self.tag_adv_word_count:
                        self.tag_adv_word_count[tag] = Counter()
                        self.tag_stu_word_count[tag] = Counter()
                    start_of_conversation = line.find(']') + 1
                    for word in line[start_of_conversation:].split(" "):
                        if not word:
                            continue
                        if ord(word[-1]) < 65 or ord(word[-1]) > 122:
                            mark = word[-1]
                            word = word[:-1]
                            self.tag_adv_word_count[tag][mark] += 1
                            #if mark == "?":
                                #advisor_asking = True
                        #if word.isdigit():
                            #word = 'info_number'
                        self.tag_adv_word_count[tag][word] += 1
                else:
                    start_of_conversation = 9
                    if last_tag == "":
                        continue
                    #if advisor_asking:
                        #for word in line[start_of_conversation:].split(" "):
                            #self.tag_stu_word_count[last_tag][word] += 1
        for tag in self.tag_adv_word_count.keys():
            self.answers.append(tag)

        for tag, freq in self.prior_count.items():
            self.prior_probability[tag] = log(freq * 1.0 / self.all_train_samples)

        for tag in self.tag_adv_word_count.keys():
            del self.tag_adv_word_count[tag][""]
            self.word_count_for_each_tag[tag] = sum(self.tag_adv_word_count[tag].values())
            self.V += self.word_count_for_each_tag[tag]


    def test(self, filename):
        golden_result = []
        my_result = []
        with open(filename, 'r') as f:
            for line in f.readlines():
                probs = {}
                for key, val in self.prior_probability.items():
                    probs[key] = val
                line = line.lower().strip()
                person = line.split(":")[0]
                if person == "advisor":
                    tag = re.search(r"\[([A-Za-z0-9_-]+)\]", line).group(1)
                    golden_result.append(tag)
                    start_of_conversation = line.find(']') + 1
                    for word in line[start_of_conversation:].split(" "):
                        if not word:
                            continue
                        if ord(word[-1]) < 65 or ord(word[-1]) > 122:
                            mark = word[-1]
                            word = word[:-1]
                            for tag in probs.keys():
                                probs[tag] += log((self.tag_adv_word_count[tag][mark] + 1.0) / (self.word_count_for_each_tag[tag] + self.V))
                        for tag in probs.keys():
                            probs[tag] += log((self.tag_adv_word_count[tag][word] + 1.0) / (self.word_count_for_each_tag[tag] + self.V))
                    res = sorted(probs.items(), key = lambda x: x[1], reverse = True)[0][0]
                    my_result.append(res)

            error_count = Counter()
            for i in xrange(len(my_result)):
                if my_result[i] != golden_result[i]:
                    error_count[(my_result[i], golden_result[i])] += 1
            print error_count.most_common(10)
        accuracy = self.evaluation(my_result, golden_result)
        print "The accuracy is %.2f" %accuracy

    def evaluation(self, my_result, golden_result):
        return accuracy_score(golden_result, my_result)

    def output_line(self, line, result):
        return line + " " + result + "\n"

if __name__ == "__main__":
    train_file = sys.argv[1]
    test_file = sys.argv[2]

    solution = DialogAct()
    solution.train(train_file)
    output_file_name = "DialogAct.test.out"
    #f = open(output_file_name, 'a')
    solution.test(test_file)