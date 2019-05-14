#!/bin/bash


# Remove quotation marks from names of directories and files
# for species_dir in ./dataset/*/; do
#     species_dir="${species_dir%/}" # remove trailing slash
#     invalid="[\"]"
#     if [[ "${species_dir}" =~ ${invalid} ]]; then
#         new_dir=$(echo ${species_dir} | tr -d '[\"]')
#         mv ${species_dir} ${new_dir}
#         echo "Moving files with quotation marks to ${new_dir}"
#         for file in $(find ${new_dir}); do
#             mv ${file} $(echo ${file} | tr -d '[\"]')
#         done
#     fi
# done

trainingDir="./trainingData"
validationDir="./validationData"

# Make sure training/validation directories exist
if [[ ! -d ${trainingDir} ]]; then
    mkdir ${trainingDir}
fi
if [[ ! -d ${validationDir} ]]; then
    mkdir ${validationDir}
fi

total_train_count=0
total_test_count=0

echo "Total training images: ${total_train_count}"
echo "Total validation images: ${total_test_count}"
# Go through the species directories
for species_dir in ./dataset/*/; do
    species_dir="${species_dir%/}" # remove trailing slash

    species_name="ERROR_NO_SPECIES_NAME"
    if [[ ${species_dir} =~ '/' ]]; then
        species_name=${species_dir##./*/}
    fi
    if [[ ${species_name} == "ERROR_NO_SPECIES_NAME" ]]; then
        echo "ERROR_NO_SPECIES_NAME for ${species_dir}"
        continue
    fi
    
    num_imgs=$(ls -1q ${species_dir}/*.jpg | wc -l) # get the number of images for this species
    echo "The number of images for ${species_dir} is ---- ${num_imgs} images"
    
    # Don't accept species with less than 100 images
    # if [[ ${num_imgs} -lt 100 ]]; then
    #     continue
    # fi
    # Only get species with images between 225 and 275 images
    if [[ ${num_imgs} -lt 225 || ${num_imgs} -gt 275 ]]; then
        continue
    fi
    
    # Create the directories necessary for each species in train/test directories
    if [[ ! -d ${trainingDir}/${species_name} ]]; then
        mkdir "${trainingDir}/${species_name}"
    fi
    if [[ ! -d ${validationDir}/${species_name} ]]; then
        mkdir "${validationDir}/${species_name}"
    fi
    
    middle=$((num_imgs / 2))
    index=1
    for img in $(find ${species_dir}/*.jpg); do # go through all images within a species directory
        if [[ ${index} -le ${middle} ]]; then
            # move to training data
            # cp ${img} "${trainingDir}/${total_train_count}.${species_name}.${index}.jpg"
            # cp ${img} "${trainingDir}/${species_name}.${total_train_count}.jpg"
            cp ${img} "${trainingDir}/${species_name}/${species_name}.${index}.jpg"
            total_train_count=$((total_train_count + 1))
        else
            # move to validation data
            # cp ${img} "${validationDir}/${total_test_count}.${species_name}.$((index - middle)).jpg"
            # cp ${img} "${validationDir}/${species_name}.${total_test_count}.jpg"
            cp ${img} "${validationDir}/${species_name}/${species_name}.$((index - middle)).jpg"
            total_test_count=$((total_test_count + 1))
        fi
        echo ${img}
        index=$((index + 1))
    done
done

echo "Total training images: ${total_train_count}"
echo "Total validation images: ${total_test_count}"

