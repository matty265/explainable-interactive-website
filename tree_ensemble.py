from dataset.adult import Adult
from os.path import exists
import numpy as np
from catboost import CatBoostClassifier, Pool, cv
from sklearn.metrics import accuracy_score


class RandomForest(CatBoostClassifier):

    def __init__(self, use_checkpoint='tree.model', iterations=10000):
        super().__init__(random_seed=42, custom_loss=['Accuracy'], iterations=iterations, logging_level='Verbose')
        if use_checkpoint is not None:
            if exists(use_checkpoint):
                super().load_model(use_checkpoint)
                self.fitted = True
            else:
                print("Path {} does not contain a valid checkpoint. Will initialize the model randomly".format(use_checkpoint))
                self.fitted = False
            

    def categorical_feature_indices(self, x):
        return np.where(x.dtypes != np.float)[0]

    def fit(self, X_train, y_train, **kwargs):
        if not self.fitted:
            cat_feature_inds = self.categorical_feature_indices(X_train)
            super().fit(X_train, y_train, cat_features=cat_feature_inds, **kwargs)
            super().save_model('tree.model')
            self.fitted = True

    def predict(self, ds, print_accuracy=False):
        X, y = ds.pandas()
        predictions = super().predict(X)
        if print_accuracy:
            print(accuracy_score(predictions, y))

        return predictions


if __name__ == "__main__":
    ds_train = Adult(None, train=True)
    ds_test = Adult(None, train=False)

    X_train, y_train = ds_train.pandas()
    X_test, y_test = ds_test.pandas()

    model = RandomForest()
    model.fit(X_train, y_train, eval_set=(X_test, y_test))
    model.predict(ds_test, print_accuracy=True)