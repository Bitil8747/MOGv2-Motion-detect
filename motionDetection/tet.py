from thundersvm import *
from sklearn.datasets import *
import time

x,y = load_svmlight_file("./data/test_dataset.txt")
clf = SVC(verbose=True, gamma=0.5, C=100)

start_time = time.time()
clf.fit(x,y)

x2,y2=load_svmlight_file("./data/test_dataset.txt")
y_predict=clf.predict(x2)
score=clf.score(x2,y2)
end_time = time.time() - start_time

print ("test score is ", score)
print ("time ", end_time)
