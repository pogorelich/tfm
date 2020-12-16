import numpy as np
from pandas import read_csv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix  
from sklearn.metrics import accuracy_score
import sys
import os

from simplejson import load as json_load

from matplotlib import pyplot as plt

if (len(sys.argv) != 2):
    print("Argumentos invalidos" + str(len(sys.argv)))
    exit(1)

config_file = sys.argv[1]
if not os.path.isfile(config_file):
    print(f"Fichero {config_file} no encontrado")
    exit(1)

with open(config_file, 'r') as f:
    config = json_load(f)

DATASET_FILES = config['DATASET_FILES']
MAX_DEPTH1    = config['MAX_DEPTH_MIN']
MAX_DEPTH2    = config['MAX_DEPTH_MAX']
MAX_DEPTH_STEP= config['MAX_DEPTH_STEP']
SEED1         = config['SEED1']
SEED2         = config['SEED2']
OUTLIERS      = config['OUTLIERS_PERCENT']
O_STEP        = config['OUTLIERS_STEP']
PCA1          = config['PCA1']
PCA2          = config['PCA2']
PCA_STEP      = config['PCA_STEP']
SAVE_DIR_     = config['SAVE_DIR']
MULTIPLICIDAD = config['MULTIPLICIDAD']

if  SAVE_DIR_[-1] != '/':
    SAVE_DIR_ += "/"

SEEDS = list(range(SEED1, SEED2+1))

b_depths = {}

# Hacer los análisis en cada conjunto
for x in range(len(DATASET_FILES)):

    DATASET_FILE = DATASET_FILES[x]

    DEPTH1       = MAX_DEPTH1[x]
    DEPTH2       = MAX_DEPTH2[x]
    DEPTH_STEP   = MAX_DEPTH_STEP[x]

    pca1         = PCA1[x]
    pca2         = PCA2[x]
    pca_step     = PCA_STEP[x]

    print("")
    print("                  " + DATASET_FILE)
    print("------------------------------------------------------------------------------------")

    dataset = read_csv(DATASET_FILE, header=None)

    array = dataset.values
    X = array[:,0:-1]
    Y = array[:,-1]

    SAVE_DIR = SAVE_DIR_ + DATASET_FILE.split('/')[-1].split('.')[0] + "/"

    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    #######################################################################################################################################
    ### ANÁLISIS MONTECARLO PARA MAX_DEPTH
    #######################################################################################################################################

    DEPTHS = list(range(DEPTH1, DEPTH2+1, DEPTH_STEP))
    if  DEPTHS[-1] != DEPTH2:
        DEPTHS.append(DEPTH2)

    depths_accuracy = []
    depths_mean_acc = np.zeros(len(DEPTHS))

    for d in range(len(DEPTHS)):
        depth = DEPTHS[d]
        depth_accuracy = np.zeros(len(SEEDS))

        for i in range(len(SEEDS)):
            seed = SEEDS[i]

            # Dividir en sets de entrenamiento y test
            validation_size = 0.20
            X_train, X_validation, Y_train, Y_validation = train_test_split(X, Y, test_size=validation_size, random_state=seed)

            # Entrenar clasificador
            model = RandomForestClassifier(max_depth=depth, random_state=seed)
            model.fit(X_train, Y_train)

            # Guardar accuracy
            acc  = model.score(X_validation, Y_validation)
            depth_accuracy[i] = acc

            # Borrar modelo
            del model

        # Guardar resultados para cada valor de MAX_DEPTH
        depth_mean = depth_accuracy.mean()
        depths_accuracy.append(depth_accuracy)
        depths_mean_acc[d] = depth_mean
        fig, ax = plt.subplots()
        plt.title("Tasa de acierto para MAX_DEPTH = %d" % (depth)) 
        ax.hist(100*depth_accuracy, bins=20, ec='black')
        props = dict(facecolor='white', alpha=10)
        ax.text(0.73, 0.92, "media: %.1f" % (100*depth_mean), transform=ax.transAxes, fontsize=12, verticalalignment='top', bbox=props)
        plt.xlabel("Tasa acierto [%]")
        plt.savefig(SAVE_DIR+f"rf_d{depth}.png", bbox_inches='tight')
        print("Depth %d: %.2f%%" % (depth, 100*depth_mean))


    # Mejor resultado medio
    b       = np.argmax(depths_mean_acc)
    b_depth = DEPTHS[b]
    b_acc   = depths_mean_acc[b]
    b_accs  = depths_accuracy[b]
    print ("Mejor resultado: Depth %d con %.2f acc" % (b_depth, 100*b_acc))
    # Agregar al diccionario
    dset = DATASET_FILE.split('/')[-1].split('.')[0].split('_')[0]
    b_depths.update({dset: b_depth})
    # Gráfica resultado analisis montecarlo
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(15,4), gridspec_kw={'width_ratios': [4, 8]})
    fig.suptitle("ANÁLISIS MONTECARLO\n%d experimentos" % (len(SEEDS)))
        # Histograma mejor resultado
    ax1.hist(100*b_accs, bins=20, ec='black')
    props = dict(facecolor='white', alpha=10)
    ax1.text(0.61, 0.92, "media: %.1f%%" % (100*b_acc), transform=ax1.transAxes, fontsize=12, verticalalignment='top', bbox=props)
    ax1.set(xlabel='Tasa acierto [%]', ylabel='Ocurrencias', title="Mejor: MAX_DEPTH=%d" % (b_depth))
        # Boxplot todos 
    ax2.boxplot(depths_accuracy)
    ax2.plot(range(1, len(DEPTHS)+1), depths_mean_acc, linestyle='-', marker='.', alpha=0.7, color='#d62728')
    ax2.set(xlabel="MAX_DEPTH", ylabel="Tasa acierto")
    ax2.set_xticklabels(DEPTHS)
        # Guardar figura
    fig.tight_layout()
    plt.subplots_adjust(wspace=0.2, top=0.84)
    fig.savefig(SAVE_DIR+'max_depth.png')


    #######################################################################################################################################
    ### ANÁLISIS MONTECARLO PARA OUTLIERS
    #######################################################################################################################################

    O_PERCENTS = list(range(0, OUTLIERS+1, O_STEP))
    if  O_PERCENTS[-1] != OUTLIERS:
        O_PERCENTS.append(OUTLIERS)

    outliers_accuracy = []
    outliers_mean_acc = np.zeros(len(O_PERCENTS))

    for p in range(len(O_PERCENTS)):
        percent = O_PERCENTS[p]
        percent_accuracy = np.zeros(len(SEEDS))

        for i in range(len(SEEDS)):
            seed = SEEDS[i]

            # Dividir en sets de entrenamiento y test
            validation_size = 0.20
            X_train, X_validation, Y_train, Y_validation = train_test_split(X, Y, test_size=validation_size, random_state=seed)

            # Introducir outliers
            n_outliers = int(percent*len(Y_train)/100)
            outliers_i = np.random.choice(len(Y_train), n_outliers, replace=False)  
            Y_train[outliers_i] = 1 - Y_train[outliers_i]

            # Entrenar clasificador
            model = RandomForestClassifier(max_depth=b_depth, random_state=seed)
            model.fit(X_train, Y_train)

            # Guardar accuracy
            acc  = model.score(X_validation, Y_validation)
            percent_accuracy[i] = acc

            # Borrar modelo
            del model

        # Guardar resultados para cada porcentaje de outliers diferente
        percent_mean = percent_accuracy.mean()
        outliers_accuracy.append(percent_accuracy)
        outliers_mean_acc[p] = percent_mean
        fig, ax = plt.subplots()
        plt.title("Tasa de acierto para %d%% de outliers" % (percent)) 
        ax.hist(100*percent_accuracy, bins=20, ec='black')
        props = dict(facecolor='white', alpha=10)
        ax.text(0.73, 0.92, "media: %.1f" % (100*percent_mean), transform=ax.transAxes, fontsize=12, verticalalignment='top', bbox=props)
        plt.xlabel("Tasa acierto [%]")
        plt.savefig(SAVE_DIR+f"rf_o{percent}.png", bbox_inches='tight')
        print("%d%% outliers: %.2f%%" % (percent, 100*percent_mean))
        

    # Mejor resultado medio
    b         = np.argmax(outliers_mean_acc)
    b_percent = O_PERCENTS[b]
    b_acc     = outliers_mean_acc[b]
    b_accs    = outliers_accuracy[b]
    print ("Mejor resultado: %d%% outliers con %.2f acc" % (b_percent, 100*b_acc))
    # Gráfica resultado analisis montecarlo
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(14,4), gridspec_kw={'width_ratios': [4, 7]})
    fig.suptitle("ANÁLISIS OUTLIERS")
        # Histograma mejor resultado
    ax1.hist(100*b_accs, bins=20, ec='black')
    props = dict(facecolor='white', alpha=10)
    ax1.text(0.61, 0.92, "media: %.1f%%" % (100*b_acc), transform=ax1.transAxes, fontsize=12, verticalalignment='top', bbox=props)
    ax1.set(xlabel='Tasa acierto [%]', ylabel='Ocurrencias', title="Mejor: %d%% outliers" % (b_percent))
        # Boxplot todos 
    ax2.boxplot(outliers_accuracy)
    ax2.plot(range(1, len(O_PERCENTS)+1), outliers_mean_acc, linestyle='-', marker='.', alpha=0.7, color='#d62728')
    ax2.set(xlabel="%% outliers", ylabel="Tasa acierto")
    ax2.set_xticklabels(O_PERCENTS)
        # Guardar figura
    fig.tight_layout()
    plt.subplots_adjust(wspace=0.2, top=0.84)
    fig.savefig(SAVE_DIR+'outliers.png')


    #######################################################################################################################################
    ### ANÁLISIS MONTECARLO PARA REDUCCIÓN DIMENSIONALIDAD CON PCA
    #######################################################################################################################################

    NCOMPS = list(range(pca1, pca2+1, pca_step))
    if  NCOMPS[-1] != pca2:
        NCOMPS.append(pca2)

    ncomps_accuracy = []
    ncomps_mean_acc = np.zeros(len(NCOMPS))

    for n in range(len(NCOMPS)):
        ncomp = NCOMPS[n]
        ncomp_accuracy = np.zeros(len(SEEDS))

        for i in range(len(SEEDS)):
            seed = SEEDS[i]

            # Dividir en sets de entrenamiento y test
            validation_size = 0.20
            X_train, X_validation, Y_train, Y_validation = train_test_split(X, Y, test_size=validation_size, random_state=seed)

            # Reducción de dimensionalidad con PCA
            pca = PCA(n_components=ncomp, svd_solver = "full", whiten=False)
            pca.fit(X_train)
            X_train              = pca.transform(X_train)
            X_validation         = pca.transform(X_validation)

            # Entrenar clasificador
            model = RandomForestClassifier(max_depth=b_depth, random_state=seed)
            model.fit(X_train, Y_train)

            # Guardar accuracy
            acc  = model.score(X_validation, Y_validation)
            ncomp_accuracy[i] = acc

            # Borrar modelo
            del model
            del pca
            
        # Guardar resultados para cada número de componentes diferente
        ncomp_mean = ncomp_accuracy.mean()
        ncomps_accuracy.append(ncomp_accuracy)
        ncomps_mean_acc[n] = ncomp_mean
        fig, ax = plt.subplots()
        plt.title("Tasa de acierto para %d componentes con PCA" % (ncomp)) 
        ax.hist(100*ncomp_accuracy, bins=20, ec='black')
        props = dict(facecolor='white', alpha=10)
        ax.text(0.73, 0.92, "media: %.1f" % (100*ncomp_mean), transform=ax.transAxes, fontsize=12, verticalalignment='top', bbox=props)
        plt.xlabel("Tasa acierto [%]")
        plt.savefig(SAVE_DIR+f"rf_n{ncomp}.png", bbox_inches='tight')
        print("%d componentes PCA: %.2f%%" % (ncomp, 100*ncomp_mean))


    # Mejor resultado medio
    b         = np.argmax(ncomps_mean_acc)
    b_ncomp   = NCOMPS[b]
    b_acc     = ncomps_mean_acc[b]
    b_accs    = ncomps_accuracy[b]
    print ("Mejor resultado: %d componentes PCA con %.2f acc" % (b_ncomp, 100*b_acc))
    # Gráfica resultado análisis montecarlo
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(14,4), gridspec_kw={'width_ratios': [4, 7]})
    fig.suptitle("ANÁLISIS REDUCCIÓN DE DIMENSIONALIDAD CON PCA")
        # Histograma mejor resultado
    ax1.hist(100*b_accs, bins=20, ec='black')
    props = dict(facecolor='white', alpha=10)
    ax1.text(0.61, 0.92, "media: %.1f%%" % (100*b_acc), transform=ax1.transAxes, fontsize=12, verticalalignment='top', bbox=props)
    ax1.set(xlabel='Tasa acierto [%]', ylabel='Ocurrencias', title="Mejor: %d componentes" % (b_ncomp))
        # Boxplot todos 
    ax2.boxplot(ncomps_accuracy)
    ax2.plot(range(1, len(NCOMPS)+1), ncomps_mean_acc, linestyle='-', marker='.', alpha=0.7, color='#d62728')
    ax2.set(xlabel="nº componentes", ylabel="Tasa acierto")
    ax2.set_xticklabels(NCOMPS)
        # Guardar figura
    fig.tight_layout()
    plt.subplots_adjust(wspace=0.2, top=0.84)
    fig.savefig(SAVE_DIR+'pca.png')


#######################################################################################################################################
### ANÁLISIS MULTIPLICIDAD
#######################################################################################################################################
# b_depths = {"dataset1": 10, "dataset2": 10, "dataset3": 10, "dataset4": 10, "dataset5": 10, "dataset6": 10, }
print(b_depths)
for comparacion in MULTIPLICIDAD:

    mults    = comparacion['M']
    files    = comparacion['FILES']
    conjunto = comparacion['CONJUNTO']

    dset     = files[0].split('/')[-1].split('.')[0].split('_')[0]

    SAVE_DIR = SAVE_DIR_ + "multiplicidad/" + dset + "/"
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    mults_accuracy = []
    mults_mean_acc = np.zeros(len(mults))

    b_depth = b_depths[dset]

    for m in range(len(mults)):
        mult    = mults[m]
        f       = files[m]
        data    = read_csv(f, header=None)
        array   = data.values
        X       = array[:,0:-1]
        Y       = array[:,-1]

        mult_accuracy = np.zeros(len(SEEDS))

        for i in range(len(SEEDS)):
            seed = SEEDS[i]

            # Dividir en sets de entrenamiento y test
            validation_size = 0.20
            X_train, X_validation, Y_train, Y_validation = train_test_split(X, Y, test_size=validation_size, random_state=seed)

            # Entrenar clasificador
            model = RandomForestClassifier(max_depth=b_depth, random_state=seed)
            model.fit(X_train, Y_train)

            # Guardar accuracy
            acc  = model.score(X_validation, Y_validation)
            mult_accuracy[i] = acc

            # Borrar modelo
            del model
            
        # Guardar resultados para cada número de componentes diferente
        mult_mean = mult_accuracy.mean()
        mults_accuracy.append(mult_accuracy)
        mults_mean_acc[m] = mult_mean
        fig, ax = plt.subplots()
        plt.title("Tasa de acierto con dataset de multiplicidad %d" % (mult)) 
        ax.hist(100*mult_accuracy, bins=20, ec='black')
        props = dict(facecolor='white', alpha=10)
        ax.text(0.73, 0.92, "media: %.1f" % (100*mult_mean), transform=ax.transAxes, fontsize=12, verticalalignment='top', bbox=props)
        plt.xlabel("Tasa acierto [%]")
        plt.savefig(SAVE_DIR+f"rf_m{mult}.png", bbox_inches='tight')
        print("Multiplicidad %d: %.2f%%" % (mult, 100*mult_mean))


    # Mejor resultado medio
    b         = np.argmax(mults_mean_acc)
    b_mult    = mults[b]
    b_acc     = mults_mean_acc[b]
    b_accs    = mults_accuracy[b]
    print ("Mejor resultado: %d componentes PCA con %.2f acc" % (b_mult, 100*b_acc))


    M = len(mults)
    print(f"M={M}")
    if M < 4:
        # Gráfica resultado análisis montecarlo
        fig, axs = plt.subplots(ncols=M, figsize=(4.6*M,4))
        fig.suptitle("ANÁLISIS MULTIPLICIDAD EN EL CONJUNTO DE DATOS " + str(conjunto))
        for i in range(M):
            ax = axs[i]
            # Histograma de cada multiplicidad
            ax.hist(100*mults_accuracy[i], bins=20, ec='black')
            props = dict(facecolor='white', alpha=10)
            ax.text(0.61, 0.92, "media: %.1f%%" % (100*mults_mean_acc[i]), transform=ax.transAxes, fontsize=12, verticalalignment='top', bbox=props)
            ax.set(xlabel='Tasa acierto [%]', ylabel='Ocurrencias', title="Multiplicidad %d" % (mults[i]))

    else:
        # Gráfica resultado análisis montecarlo
        fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(14,4), gridspec_kw={'width_ratios': [4, 7]})
        fig.suptitle("ANÁLISIS MULTIPLICIDAD EN EL CONJUNTO DE DATOS " + str(conjunto))
            # Histograma mejor resultado
        ax1.hist(100*b_accs, bins=20, ec='black')
        props = dict(facecolor='white', alpha=10)
        ax1.text(0.61, 0.92, "media: %.1f%%" % (100*b_acc), transform=ax1.transAxes, fontsize=12, verticalalignment='top', bbox=props)
        ax1.set(xlabel='Tasa acierto [%]', ylabel='Ocurrencias', title="Mejor: multiplicidad %d" % (b_mult))
            # Boxplot todos 
        ax2.boxplot(mults_accuracy)
        ax2.plot(range(1, len(mults)+1), mults_mean_acc, linestyle='-', marker='.', alpha=0.7, color='#d62728')
        ax2.set(xlabel="multiplicidad", ylabel="Tasa acierto")
        ax2.set_xticklabels(mults)

        # Guardar figura
    fig.tight_layout()
    plt.subplots_adjust(wspace=0.2, top=0.84)
    fig.savefig(SAVE_DIR+'mul.png')




