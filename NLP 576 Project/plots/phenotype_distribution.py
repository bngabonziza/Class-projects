import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def correlation_plot(np_mat, labels):
    '''

    :param np_mat: The numpy matrix holding the correlation values
    :param labels: The labels include the strings of the phenotypes
    :return:
    '''
    d = pd.DataFrame(data=np_mat,
                     columns=labels)

    # Compute the correlation matrix
    corr = d.corr()

    # Generate a mask for the upper triangle
    mask = np.zeros_like(corr, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    # Generate a custom diverging colormap
    # cmap = sns.diverging_palette(220, 10, as_cmap=True)
    cmap = 'Greys'

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(corr, mask=mask, cmap=cmap, vmin=0., vmax=1.,
                square=True, linewidths=.5, cbar_kws={"shrink": .5})
    plt.yticks(rotation=0)
    plt.xticks(rotation=90)

    plt.show()

def phen_dist(data, xTicks):
    yLabels = '# Patients'
    xLabels = 'Phenotype'
    hfont = {'fontname': 'Arial'}
    ind = np.arange(len(data))
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111)


    width = 0.35
    # print(data)
    rects1 = ax.bar(ind, data, width,
                    color='#0000ff')  # axes and labels
    ax.set_xlim(-width, len(ind) + width)
    # ax.set_ylim(87, 95)
    ax.set_ylabel(yLabels, size=30, **hfont)
    ax.set_xlabel(xLabels, size=30, **hfont)
    ax.set_xticks(ind)
    xtickNames = ax.set_xticklabels(xTicks, **hfont)
    plt.setp(xtickNames, rotation=45, fontsize=5, ha='right')
    plt.grid(True)
    plt.xticks(size=20)
    plt.yticks(size=20)
    # plt.subplots_adjust(left=0.13, bottom=0.30, top=0.9)
    plt.subplots_adjust(left=0.13, bottom=0.28, top=0.9)
    ## add a legend
    # ax.legend( (rects1[0], ('Men', 'Women') )

    plt.show()
    plt.close()

if __name__ == "__main__":
    df = pd.read_csv(open('../data/outputs/Labels_All.csv'))

    data = []
    phenotypes = ['Asthma', 'CAD', 'CHF', 'Depression', 'Diabetes',
                       'Gallstones', 'GERD', 'Gout', 'Hypercholesterolemia',
                       'Hypertension', 'Hypertriglyceridemia', 'OA', 'Obesity',
                       'OSA', 'PVD', 'Venous Insufficiency']  # also referred to as diseases

    labels = []
    for c in phenotypes:
        df_ph = df[df[c] == 1.]
        # data.append(df['id'])
        data.append(len(df_ph['id']))
        labels.append(c)

    phen_dist(data, labels)

    # rs = np.random.RandomState(33)
