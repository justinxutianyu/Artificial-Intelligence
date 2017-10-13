import matplotlib.pyplot as plt
import numpy as np

from scipy.stats import norm, binom

def powerScale(values, target, k):
    expDist = [
        powerTransform(
            val, min(values), max(values),
            min(target), max(target), k
        )
        for val in values
    ]
    return expDist

def linearScale(values, target):
    return [
        linearTransform(
            val, min(values), max(values),
            min(target), max(target)
        )
        for val in values
    ]

def normalScale(values):
    dist = norm(loc=np.mean(values), scale=np.std(values))
    return [dist.cdf(val) for val in values]

def binomScale(values):
    return None

def powerTransform(value, leftmin, leftmax, rightmin, rightmax, k):
    leftSpan  = leftmax - leftmin
    rightSpan = rightmax - rightmin

    valueScaled = float(value - leftmin) / float(leftSpan)

    return rightmin + ((valueScaled ** k) * rightmax)

def linearTransform(value, leftmin, leftmax, rightmin, rightmax):
    # Figure out how 'wide' each range is
    leftSpan  = leftmax - leftmin
    rightSpan = rightmax - rightmin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftmin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightmin + (valueScaled * rightmax)

def readPs(infile):
    ps = []
    with open(infile) as file:
        file.next()
        for line in file:
            ps.append(float(line.split(",")[1].strip()))
    return ps

def writeLinearPs(ps, outfile):
    with open(outfile, 'w') as file:
        ids = range(1, len(ps) + 1)
        file.write("Id,Prediction\n")
        plt.scatter(ids, ps)
        plt.show()
        transformed = linearScale(ps, [0, 1])
        plt.scatter(ids, transformed)
        plt.show()
        for id,p in zip(ids, transformed):
            file.write("{},{}\n".format(id, p))
    print("Done!")

def writeNormalPs(ps, outfile):
    with open(outfile, 'w') as file:
        ids = range(1, len(ps) + 1)
        file.write("Id,Prediction\n")
        plt.scatter(ids, ps)
        plt.show()
        transformed = normalScale(ps)
        plt.scatter(ids, transformed)
        plt.show()
        for id,p in zip(ids, transformed):
            file.write("{},{}\n".format(id, p))
    print("Done!")

def writeBinomPs(ps, outfile):
    with open(outfile, 'w') as file:
        ids = range(1, len(ps) + 1)
        file.write("Id,Prediction\n")
        plt.scatter(ids, ps)
        plt.show()
        transformed = binomScale(ps)
        plt.scatter(ids, transformed)
        plt.show()
        for id,p in zip(ids, transformed):
            file.write("{},{}\n".format(id, p))
    print("Done!")

def main():
    #Read in the raw probabilities
    ps = readPs("../predictions/fromto_intersect_predicitons_raw.csv")
    #Transform the raw probabilities using various distributions
    #writeLinearPs(ps, "../predictions/intersect_predictions_linear.csv")
    writeNormalPs(ps, "../predictions/fromto_intersect_predictions_normal.csv")
    #writeBinomPs(ps, "../predictions/intersect_predictions_binom.csv")

if __name__ == "__main__":
    main()
