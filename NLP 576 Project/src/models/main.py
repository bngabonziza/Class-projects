import argparse
from EHR_Parse import *
from label_analysis import *
import os
import pandas as pd
from plots.phenotype_distribution import *

def main():
    '''

    :return:
    '''
    parser = argparse.ArgumentParser(description='Optional description')

    parser.add_argument('pos_arg', type=str,
                        help='EHR/Label documents')

    parser.add_argument('--inpPath', type=str,
                        help='An optional (but required) input path for the documents')

    parser.add_argument('--outPath', type=str,
                        help='An optional output path for the processed documents')

    parser.add_argument('--splitSaveEHR', type=bool,
                        help='An optional argument (1/0) to assert whether EHR sections should be stored in different files'
                             'or in the same file ')

    args = parser.parse_args()

    outputPath = args.outPath
    df_list = []

    if args.pos_arg == 'EHR':
        # Save the different files
        for files in os.listdir(args.inpPath):
            ehrP = EHR_Parse(args.inpPath + files)
            ehrP.splitRecord()
            df_list.append(ehrP.saveFile())

        df_final = pd.concat(df_list,  ignore_index=True)
        outputPath = args.outPath

        df_final.to_csv(outputPath + 'EHR_records_All_v4_17' + '.csv')
    else:
        ehrL = Labels()
        for files in os.listdir(args.inpPath):
            ehrL.doc_parse(args.inpPath + files)

        # for id in range(1, 1237):
        #     if id not in ehrL.doc_lab_map.keys():
        #         print(id)
            # df_list.append(ehrL.save_file())

        ''' Get the correlation matrix and show the plot '''
        # corrMat, labels = ehrL.label_distribution()
        # correlation_plot(corrMat, labels)


        ''' To save the final concatenated files'''
        # df_final = pd.concat(df_list, ignore_index=True)
        # outputPath = args.outPath
        #
        # df_final.to_csv(outputPath + 'Labels_All' + '.csv')

if __name__ == "__main__":
    main()

