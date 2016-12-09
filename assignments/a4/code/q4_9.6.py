import numpy as np
import matplotlib.pyplot as plt
import itertools
from collections import OrderedDict
from sklearn import datasets
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.multiclass import OneVsRestClassifier, OneVsOneClassifier


def parse_classification_report(clfreport):
    # https://gist.github.com/julienr/6b9b9a03bd8224db7b4f
    """
    Parse a sklearn classification report into a dict keyed by class name
    and containing a tuple (precision, recall, fscore, support) for each class
    """
    lines = clfreport.split('\n')
    # Remove empty lines
    lines = list(filter(lambda l: not len(l.strip()) == 0, lines))

    # Starts with a header, then score for each class and finally an average
    header = lines[0]
    cls_lines = lines[1:-1]
    avg_line = lines[-1]

    assert header.split() == ['precision', 'recall', 'f1-score', 'support']
    assert avg_line.split()[0] == 'avg'

    # We cannot simply use split because class names can have spaces. So instead
    # figure the width of the class field by looking at the indentation of the
    # precision header
    cls_field_width = len(header) - len(header.lstrip())

    # Now, collect all the class names and score in a dict
    def parse_line(l):
        """Parse a line of classification_report"""
        cls_name = l[:cls_field_width].strip()
        precision, recall, fscore, support = l[cls_field_width:].split()
        precision = float(precision)
        recall = float(recall)
        fscore = float(fscore)
        support = int(support)
        return cls_name, precision, recall, fscore, support

    data = OrderedDict()
    for l in cls_lines:
        ret = parse_line(l)
        cls_name = ret[0]
        scores = ret[1:]
        data[cls_name] = scores

    # average
    data['avg'] = parse_line(avg_line)[1:]

    return data


def report_to_latex_table(clfreport):
    data = parse_classification_report(clfreport)
    out = ""
    out += "\\begin{tabular}{c | c c c c}\n"
    out += "Class & Precision & Recall & F-score & Support\\\\\n"
    out += "\hline\n"
    out += "\hline\\\\\n"
    for cls, scores in data.items():
        out += cls + " & " + " & ".join([str(s) for s in scores])
        out += "\\\\\n"
    out += "\\end{tabular}"
    return out


def plot_classification():
    # modified http://scikit-learn.org/stable/auto_examples/svm/plot_iris.html#sphx-glr-auto-examples-svm-plot-iris-py
    iris = datasets.load_iris()
    X = iris.data[:, :2] # only want  to classify what type of iris it is
    y = iris.target
    C = 1.0  # SVM regularization parameter
    h = .02  # step size in the mesh

    svm_c = OneVsOneClassifier(SVC(kernel='linear', C=C))
    svm_l = OneVsRestClassifier(LinearSVC(C=C))

    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))

    titles = ['One-vs-One', 'One-vs-All']

    plt.suptitle('Linear SVM')

    # Plot the decision boundary. For that, we will assign a color to each
    # point in the mesh [x_min, x_max]x[y_min, y_max].
    plt.subplot(1, 2, 0 + 1)
    plt.subplots_adjust(wspace=0.4, hspace=0.4)

    Z_c = svm_c.fit(X, y).predict(np.c_[xx.ravel(), yy.ravel()])

    # Put the result into a color plot
    Z_c = Z_c.reshape(xx.shape)
    plt.contourf(xx, yy, Z_c, cmap=plt.cm.coolwarm, alpha=0.8)

    # Plot also the training points
    plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.coolwarm)
    plt.xlabel('Sepal length')
    plt.ylabel('Sepal width')
    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())
    plt.xticks(())
    plt.yticks(())
    plt.title(titles[0])

    # Plot the decision boundary. For that, we will assign a color to each
    # point in the mesh [x_min, x_max]x[y_min, y_max].
    plt.subplot(1, 2, 1 + 1)
    plt.subplots_adjust(wspace=0.4, hspace=0.4)

    Z_l = svm_l.fit(X, y).predict(np.c_[xx.ravel(), yy.ravel()])

    # Put the result into a color plot
    Z_l = Z_l.reshape(xx.shape)
    plt.contourf(xx, yy, Z_l, cmap=plt.cm.coolwarm, alpha=0.8)

    # Plot also the training points
    plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.coolwarm)
    plt.xlabel('Sepal length')
    plt.ylabel('Sepal width')
    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())
    plt.xticks(())
    plt.yticks(())
    plt.title(titles[1])

    plt.savefig('images/svm_linear_1v1_1va.png')
    plt.close()


def plot_confusion_matrix(cm, classes, normalize=False, title='Confusion matrix', cmap=plt.cm.Blues,showC=True):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    if showC:
        plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print(title)
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


def evaluation():
    iris = datasets.load_iris()
    class_names = iris.target_names
    C = 1.0  # SVM regularization parameter
    X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.4, random_state=0)

    svm_c = OneVsOneClassifier(SVC(kernel='linear', C=C))
    y_pred = svm_c.fit(X_train, y_train).predict(X_test)

    with open('output_files/svm_1v1_classification_report.tex', 'w') as out:
        out.write('\\begin{table}\n')
        out.write(report_to_latex_table(classification_report(y_test, y_pred, target_names=iris.target_names)))
        out.write('\n\\end{table}\n')

    # Compute confusion matrix
    cnf_matrix = confusion_matrix(y_test, y_pred)
    np.set_printoptions(precision=2)

    # Plot normalized confusion matrix
    plt.figure()
    plot_confusion_matrix(cnf_matrix, classes=class_names, normalize=True,
                          title='SVM One-vs-One Confusion Matrix')
    plt.tight_layout()
    plt.savefig('images/svm_linear_1v1_cm.png')
    plt.close()

    svm_l = OneVsRestClassifier(LinearSVC(C=C))
    y_pred = svm_l.fit(X_train, y_train).predict(X_test)
    with open('output_files/svm_1va_classification_report.tex', 'w') as out:
        out.write('\\begin{table}\n')
        out.write(report_to_latex_table(classification_report(y_test, y_pred, target_names=iris.target_names)))
        out.write('\n\\end{table}\n')

    # Compute confusion matrix
    cnf_matrix = confusion_matrix(y_test, y_pred)
    np.set_printoptions(precision=2)

    # Plot normalized confusion matrix
    plt.figure()
    plot_confusion_matrix(cnf_matrix, classes=class_names, normalize=True,
                          title='SVM One-vs-All Confusion Matrix',showC=False)

    plt.tight_layout()
    plt.savefig('images/svm_linear_1va_cm.png')
    plt.close()


if __name__ == '__main__':
    plot_classification()
    evaluation()
