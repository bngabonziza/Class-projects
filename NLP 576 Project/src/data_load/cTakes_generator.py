import os

if __name__ == '__main__':

    cTakesPath = "C:/PhD/Courses/NLP/Project/cTakes/apache-ctakes-4.0.0/bin/"
    inputFilesPath = "C:/PhD/Courses/NLP/Project/python_scripts/input_files/"
    outputFilesPath = "C:/PhD/Courses/NLP/Project/python_scripts/output_files/"

    os.chdir(cTakesPath)
    os.system("start /B start cmd.exe @cmd /k" "runClinicalPipeline_1 -i " + inputFilesPath + " --xmiOut " + outputFilesPath + " --user soumajyoti --pass Impossible2")

    print "CTakes is being executed ..."
    print "Script done."