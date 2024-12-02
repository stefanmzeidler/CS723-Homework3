import os
from unittest import case

import pandas as pd
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from pickle import dump,load

#

# count_vect = CountVectorizer()
# X_train_counts = count_vect.fit_transform(twenty_train.data)
text_clf = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), (
    'clf', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, random_state=42, max_iter=5, tol=None))])


#
# twenty_test = fetch_20newsgroups(subset='test', categories=categories, shuffle=True, random_state=42)
# text_clf.fit(twenty_train.data, twenty_train.target)
# docs_test = twenty_test.data
# predicted = text_clf.predict(docs_test)
# print(metrics.classification_report(twenty_test.target, predicted,target_names=twenty_test.target_names))


class CLFTrainer:
    def __init__(self, data_file: str = None):
        self.data = pd.read_csv(data_file, sep=None, engine='python', names=['features', 'target'], header=0,
                                usecols=[1, 2],encoding_errors = 'replace')
        # print(self.data.head())
        self.features = self.data['features']
        self.target = self.data['target']
        print(self.target.value_counts())
        # self.x_test, self.y_test, self.x_training, self.x_validation, self.y_training, self.y_validation = self.__split_data()

    def __split_data(self):
        """
        Split the dataset into 80% training and 20% testing sets. The training set is further split into 80% training and 20% validation sets.
        :return: Returns the x and y test, training, and validation sets.
        """
        x_tr, x_test, y_tr, y_test = train_test_split(self.features, self.target, test_size=0.2, random_state=3)
        x_training, x_validation, y_training, y_validation = train_test_split(x_tr, y_tr, test_size=0.2, random_state=3)
        return x_test, y_test, x_training, x_validation, y_training, y_validation

    def train_model(self, save = True):
        model_pipe = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), (
            'clf', SGDClassifier(loss='hinge'))])
        parameters = {'vect__ngram_range': [(1, 1), (1, 2),(1,3)], 'tfidf__use_idf': (True, False),
            'clf__alpha': (1e-2, 1e-3)}
        text_classifier = GridSearchCV(model_pipe, parameters, cv=10, return_train_score=True)
        text_classifier.fit(self.features, self.target)
        best_model = text_classifier.best_estimator_
        results = pd.DataFrame(text_classifier.cv_results_)
        if save:
            with open("sentiment_classifier.pkl", "wb") as f:
                dump(best_model, f, protocol=5)
        return best_model

class ModelTester:
    def __init__(self,model):
        self.model = model

    def test(self, text):
        prediction = self.model.predict([text])
        match prediction:
            case 0:
                return 'sad'
            case 1:
                return 'joy'
            case 2:
                return 'love'
            case 3:
                return 'anger'
            case 4:
                return 'fear'
            case 5:
                return 'surprise'



def main():
    cur_dir = os.path.dirname(__file__)
    classifier_file = os.path.join(cur_dir, 'sentiment_classifier.pkl')
    if os.path.isfile(classifier_file):
        with open((os.path.join(cur_dir, 'sentiment_classifier.pkl')), 'rb') as f:
            classifier = load(f)
    else:
        filepath = os.path.join(cur_dir, 'Datasets', 'Emotions_Dataset.csv')
        my_trainer = CLFTrainer(filepath)
        classifier = my_trainer.train_model()
    my_tester = ModelTester(classifier)
    while True:
        response = input("Please enter a statement or type 'exit' to exit:")
        if response == 'exit':
            break
        print(my_tester.test(response))


main()
