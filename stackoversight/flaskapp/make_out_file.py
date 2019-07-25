# this script will take output of program and make a file that will be passed into the flask app
from database_connect import find_snippet_qid
# list of snippets i got
list_of_snippets=[]   #

# mylist will be a list of max 3 snippets that match the most
mylist = list_of_snippets

if len(mylist) >= 1:
    best_snippet = mylist[0]
    seq1 = ["Best Match :\n", best_snippet, "\n"]
    question_id1 = find_snippet_qid(best_snippet)
if len(mylist) >= 2 :
    second_best_snippet = mylist[1]
    seq2 = ["Second best Match :\n", second_best_snippet, "\n"]
    question_id2 = find_snippet_qid(second_best_snippet)
if len(mylist) >= 3 :
    third_best_snippet = mylist[2]
    seq3 = ["Third best Match :\n", third_best_snippet, "\n"]
    question_id3 = find_snippet_qid(third_best_snippet)


def write_qid(qid_list):
    for i in qid_list:
        new_file.write(f"https://stackoverflow.com/questions/{i}\n")
    new_file.write("\n\n")

def write_in_file(len):
    if len >= 1:
        new_file.writelines(seq1)
        write_qid(question_id1)
    if len >= 2:
        new_file.writelines(seq2)
        write_qid(question_id2)
    if len >= 3:
        new_file.writelines(seq3)
        write_qid(question_id3)


# make a file and write into it
try:
    new_file = open("some_file.txt", "w+")
    # write_in_file(mylist.count())
except IOError:
    print("prolem oepnning or reading writing in a file!")
finally:
    new_file.close()



