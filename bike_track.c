#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAX_RECORDS 100
#define MAX_COMPONENTS 9

typedef struct {
    char date[11];
    char description[256];
} MaintenanceRecord;

typedef struct {
    char name[50];
    int wearLevel; // 0 to 100, where 0 means new and 100 means fully worn out
} Component;

MaintenanceRecord records[MAX_RECORDS];
Component components[MAX_COMPONENTS] = {
    {"Front Tire", 0},
    {"Rear Tire", 0},
    {"Front Inner Tube", 0},
    {"Rear Inner Tube", 0},
    {"Front Derailleur Cable", 0},
    {"Rear Derailleur Cable", 0},
    {"Front Brake Cable", 0},
    {"Rear Brake Cable", 0},
    {"Handlebar Tape", 0}
};

int recordCount = 0;
double bikeWeight = 0.0;

void loadRecords() {
    FILE* file = fopen("records.txt", "r");
    if (file == NULL) {
        printf("No maintenance records found.\n");
        return;
    }
    fscanf(file, "%d\n", &recordCount);
    for (int i = 0; i < recordCount; i++) {
        fscanf(file, "%10s\n", records[i].date);
        fgets(records[i].description, 256, file);
        records[i].description[strcspn(records[i].description, "\n")] = 0; // remove newline character
    }
    fclose(file);
}

void saveRecords() {
    FILE* file = fopen("records.txt", "w");
    if (file == NULL) {
        printf("Error saving records.\n");
        return;
    }
    fprintf(file, "%d\n", recordCount);
    for (int i = 0; i < recordCount; i++) {
        fprintf(file, "%s\n", records[i].date);
        fprintf(file, "%s\n", records[i].description);
    }
    fclose(file);
}

void loadComponents() {
    FILE* file = fopen("components.txt", "r");
    if (file == NULL) {
        printf("No components data found.\n");
        return;
    }
    fscanf(file, "%lf\n", &bikeWeight);
    for (int i = 0; i < MAX_COMPONENTS; i++) {
        fscanf(file, "%d\n", &components[i].wearLevel);
    }
    fclose(file);
}

void saveComponents() {
    FILE* file = fopen("components.txt", "w");
    if (file == NULL) {
        printf("Error saving components.\n");
        return;
    }
    fprintf(file, "%.2f\n", bikeWeight);
    for (int i = 0; i < MAX_COMPONENTS; i++) {
        fprintf(file, "%d\n", components[i].wearLevel);
    }
    fclose(file);
}

void addRecord() {
    if (recordCount >= MAX_RECORDS) {
        printf("No more space for new records.\n");
        return;
    }
    printf("Enter date (YYYY-MM-DD): ");
    scanf("%10s", records[recordCount].date);
    getchar(); // consume newline character
    printf("Enter description: ");
    fgets(records[recordCount].description, 256, stdin);
    records[recordCount].description[strcspn(records[recordCount].description, "\n")] = 0; // remove newline character
    recordCount++;
    saveRecords();
    printf("Record added successfully!\n");
}

void viewRecords() {
    loadRecords(); // Ensure records are reloaded from the file
    if (recordCount == 0) {
        printf("No maintenance records found.\n");
    }
    else {
        printf("Maintenance Records:\n");
        for (int i = 0; i < recordCount; i++) {
            printf("Date: %s, Description: %s\n", records[i].date, records[i].description);
        }
    }
}

void updateBikeWeight() {
    printf("Enter the bike weight (kg): ");
    scanf("%lf", &bikeWeight);
    saveComponents();
    printf("Bike weight updated successfully!\n");
}

void viewBikeWeight() {
    loadComponents(); // Ensure components data is reloaded from the file
    printf("Bike Weight: %.2f kg\n", bikeWeight);
}

void viewComponents() {
    loadComponents(); // Ensure components data is reloaded from the file
    printf("Bike Components and Their Wear Levels:\n");
    for (int i = 0; i < MAX_COMPONENTS; i++) {
        printf("%s (Wear Level: %d%%)\n", components[i].name, components[i].wearLevel);
    }
}

void updateComponentWearLevel() {
    printf("Select a component to update wear level:\n");
    for (int i = 0; i < MAX_COMPONENTS; i++) {
        printf("%d. %s\n", i + 1, components[i].name);
    }
    printf("Choose an option: ");
    int choice;
    scanf("%d", &choice);
    if (choice >= 1 && choice <= MAX_COMPONENTS) {
        printf("Enter new wear level (0-100%%): ");
        int wearLevel;
        scanf("%d", &wearLevel);
        if (wearLevel >= 0 && wearLevel <= 100) {
            components[choice - 1].wearLevel = wearLevel;
            saveComponents();
            printf("Wear level updated successfully!\n");
        }
        else {
            printf("Invalid wear level. Please try again.\n");
        }
    }
    else {
        printf("Invalid choice. Please try again.\n");
    }
}

void showMenu() {
    printf("\nBike Maintenance Tracker\n");
    printf("1. Add Maintenance Record\n");
    printf("2. View Maintenance Records\n");
    printf("3. Update Bike Weight\n");
    printf("4. View Bike Weight\n");
    printf("5. View Components and Wear Levels\n");
    printf("6. Update Component Wear Level\n");
    printf("7. Exit\n");
    printf("Choose an option: ");
}

int main() {
    loadRecords();
    loadComponents();
    while (1) {
        showMenu();
        int choice;
        scanf("%d", &choice);
        getchar(); // consume newline character
        switch (choice) {
        case 1:
            addRecord();
            break;
        case 2:
            viewRecords();
            break;
        case 3:
            updateBikeWeight();
            break;
        case 4:
            viewBikeWeight();
            break;
        case 5:
            viewComponents();
            break;
        case 6:
            updateComponentWearLevel();
            break;
        case 7:
            printf("Exiting... Goodbye!\n");
            return 0;
        default:
            printf("Invalid choice. Please try again.\n");
        }
    }
}
