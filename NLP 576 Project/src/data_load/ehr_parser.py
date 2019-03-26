import csv

if __name__ == '__main__':

    with open('./ehr/EHR_records_All.csv') as csvfile:
        lines = csv.reader(csvfile, delimiter=',')
        records = list(lines)
        csvfile.seek(0)

        for i, fields in enumerate(lines):

            if i > 0:

                print str(i) + " out of " + str(len(records) - 1)

                id = fields[0]
                principal_diagnosis = fields[2]
                secondary_diagnoses = fields[3]
                history_of_present_illness = fields[4]
                pre_admission_medications = fields[5]
                past_medical_history = fields[6]
                family_history = fields[7]
                social_history = fields[8]
                allergies = fields[9]
                admission_physical_examination = fields[10]
                discharge_medications = fields[11]

                output_file = open("./input_files/ehr_" + format(int(id), '03d') + "_pri",'w')
                output_file.write(principal_diagnosis.strip())
                output_file.close()

                output_file = open("./input_files/ehr_" + format(int(id), '03d') + "_sec",'w')
                output_file.write(secondary_diagnoses.strip())
                output_file.close()

                output_file = open("./input_files/ehr_" + format(int(id), '03d') + "_his",'w')
                output_file.write(history_of_present_illness.strip())
                output_file.close()

                output_file = open("./input_files/ehr_" + format(int(id), '03d') + "_pre",'w')
                output_file.write(pre_admission_medications.strip())
                output_file.close()

                output_file = open("./input_files/ehr_" + format(int(id), '03d') + "_pas",'w')
                output_file.write(past_medical_history.strip())
                output_file.close()

                output_file = open("./input_files/ehr_" + format(int(id), '03d') + "_fam",'w')
                output_file.write(family_history.strip())
                output_file.close()

                output_file = open("./input_files/ehr_" + format(int(id), '03d') + "_soc",'w')
                output_file.write(social_history.strip())
                output_file.close()

                output_file = open("./input_files/ehr_" + format(int(id), '03d') + "_all",'w')
                output_file.write(allergies.strip())
                output_file.close()

                output_file = open("./input_files/ehr_" + format(int(id), '03d') + "_adm",'w')
                output_file.write(admission_physical_examination.strip())
                output_file.close()

                output_file = open("./input_files/ehr_" + format(int(id), '03d') + "_dis",'w')
                output_file.write(discharge_medications.strip())
                output_file.close()