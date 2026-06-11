import operator
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import confusion_matrix, accuracy_score, precision_score,recall_score, f1_score

epsilon = 1e-8
class FuzzyKnn(BaseEstimator, ClassifierMixin):
    def __init__(self,m=2, k=None, plot=False):
        self.k = k
        self.m = m
        self.plot = plot
        self.epsilon = epsilon
    # menentukan nilai k tahap 1
    def set_k(self,new_k):
        if type(new_k) != int or new_k % 2 == 0 or new_k <= 0:
           raise ValueError("k harus bilangan ganjil positif")
        self.k = new_k
    
    def fit(self, X, y=None):
        self._check_params(X, y)
        self.X = X
        self.y = y
        self.xdim = len(self.X[0])
        self.n = len(y)
        classes = list(set(y))
        classes.sort()
        self.classes = classes
        self.df = pd.DataFrame(self.X)
        self.df['y'] = self.y
        self.memberships = self._compute_memberships()
        self.df['membership'] = self.memberships
        self.fitted_ = True
        return self
# menghitung nilai keanggotaan tahap 6
    def predict(self, X):
      if self.fitted_ is None:
          raise Exception('predict() called before fit()')
      else:
          m = self.m
          y_pred = []
          for x in X:
              neighbors = self._find_k_nearest_neighbors(pd.DataFrame.copy(self.df), x)
              votes = {}
              for c in self.classes:
                  den = 0
                  for n in range(self.k):
                      dist = np.linalg.norm(x - neighbors.iloc[n, 0:self.xdim])
                      den += 1 / (dist ** (2 / (m - 1))+ epsilon)
                  neighbors_votes = []
                  for n in range(self.k):
                      dist = np.linalg.norm(x - neighbors.iloc[n, 0:self.xdim])
                      num = (neighbors.iloc[n].membership[c]) / (dist ** (2 / (m - 1))+ epsilon)
                      vote = num / den
                      neighbors_votes.append(vote)
                  votes[c] = np.sum(neighbors_votes)
            # memilih kelas dengan nilai keanggotaan terbesar tahap 7
              pred = max(votes.items(), key=operator.itemgetter(1))[0]
              y_pred.append(pred)
          return y_pred
    def predict_top_membership(self, X):
        hasil_semua = []

        for x in X:
            neighbors = self._find_k_nearest_neighbors(pd.DataFrame.copy(self.df), x)
            votes = {}

            for c in self.classes:
                den = 0

                for n in range(self.k):
                    dist = np.linalg.norm(x - neighbors.iloc[n, 0:self.xdim])
                    den += 1 / (dist ** (2 / (self.m - 1)) + self.epsilon)

                nilai_votes = []

                for n in range(self.k):
                    dist = np.linalg.norm(x - neighbors.iloc[n, 0:self.xdim])
                    num = neighbors.iloc[n].membership[c] / (
                        dist ** (2 / (self.m - 1)) + self.epsilon
                    )
                    nilai_votes.append(num / den)

                votes[c] = np.sum(nilai_votes)

            hasil_urut = sorted(
                votes.items(),
                key=lambda x: x[1],
                reverse=True
            )

            hasil_semua.append(hasil_urut)

        return hasil_semua

      
# menghitung nilai ecluidian distance tahap 2
    def _find_k_nearest_neighbors(self, df, x):
        X = df.iloc[:, 0:self.xdim].values
        df['distances'] = [np.linalg.norm(X[i] - x) for i in range(self.n)]
        # mengurutkan jarak terkecil ke terbesar tahap 3
        df.sort_values(by='distances', ascending=True, inplace=True)
        # menentukan nilai k tetangga terdekat tahap 4
        neighbors = df.iloc[0:self.k]
        return neighbors

    def _get_counts(self, neighbors):
        groups = neighbors.groupby('y')
        counts = {g['y'].iloc[0]: len(g) for _, g in groups}
        return counts

# menentukan nilai keanggotaan awal (fuzzy) tahap 5
    def _compute_memberships(self):
        memberships = []
        for i in range(self.n):
            x = self.X[i]
            y = self.y[i]
            neighbors = self._find_k_nearest_neighbors(pd.DataFrame.copy(self.df), x)
            counts = self._get_counts(neighbors)
            membership = dict()
            for c in self.classes:
                try:
                    uci = 0.49 * (counts[c] / self.k)
                    if c == y:
                        uci += 0.51
                    membership[c] = uci
                except:
                    membership[c] = 0
            memberships.append(membership)
        return memberships

    def _check_params(self, X, y):
        if type(self.k) != int:
            raise Exception('"k" should have type int')
        if self.k >= len(y):
            raise Exception('"k" should be less than the number of feature sets')
        if self.k % 2 == 0:
            raise Exception('"k" should be odd')
        if type(self.plot) != bool:
            raise Exception('"plot" should have type bool')
    # Function untuk menampilkan 3 penyakit terdekat
    