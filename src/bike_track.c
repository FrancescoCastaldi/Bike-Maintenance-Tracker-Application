/**
 * bike_track.c - Bike Maintenance Tracker (CLI)
 * 
 * A lightweight command-line tool to manage bike maintenance records,
 * track bike weight, and monitor component wear levels.
 * 
 * Data is persisted in:
 *   - records.txt     (maintenance history)
 *   - components.txt  (component wear percentages)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_RECORDS     256
#define MAX_DESC_LEN    512
#define DATE_LEN        16
#define FILENAME_RECORDS    "records.txt"
#define FILENAME_COMPONENTS "components.txt"

/* ----- Data Structures ----- */
typedef struct {
    char date[DATE_LEN];
    char description[MAX_DESC_LEN];
} MaintenanceRecord;

typedef struct {
    char name[64];
    int  wear_percent; /* 0 = new, 100 = worn out */
} BikeComponent;

/* ----- Global State ----- */
static MaintenanceRecord records[MAX_RECORDS];
static int record_count = 0;

static BikeComponent components[] = {
    {"Tyres",              50},
    {"Inner Tubes",        50},
    {"Derailleur Cables",  50},
    {"Brake Cables",       50},
    {"Handlebar Tape",     50}
};
static int component_count = 5;

static float bike_weight_kg = 8.5f;

/* ----- Prototypes ----- */
static void clear_input_buffer(void);
static void load_records(void);
static void save_records(void);
static void load_components(void);
static void save_components(void);
static void show_menu(void);
static void add_record(void);
static void view_records(void);
static void update_weight(void);
static void view_weight(void);
static void view_components(void);
static void update_component(void);

/* ================================================================
 *  Main
 * ================================================================ */
int main(void) {
    int choice;

    load_records();
    load_components();

    printf("\n");
    printf("  ==========================================\n");
    printf("     🚴  BIKE MAINTENANCE TRACKER (CLI)    \n");
    printf("  ==========================================\n\n");

    do {
        show_menu();
        printf("  Your choice: ");
        if (scanf("%d", &choice) != 1) {
            choice = 0;
        }
        clear_input_buffer();
        printf("\n");

        switch (choice) {
            case 1:  add_record();          break;
            case 2:  view_records();        break;
            case 3:  view_weight();         break;
            case 4:  update_weight();       break;
            case 5:  view_components();     break;
            case 6:  update_component();    break;
            case 0:  printf("  👋 Goodbye! Keep riding!\n\n"); break;
            default: printf("  ⚠️  Invalid choice. Try again.\n\n");
        }
    } while (choice != 0);

    save_records();
    save_components();
    return 0;
}

/* ----- Utility ----- */
static void clear_input_buffer(void) {
    int c;
    while ((c = getchar()) != '\n' && c != EOF) {}
}

/* ----- File I/O : Records ----- */
static void load_records(void) {
    FILE *fp = fopen(FILENAME_RECORDS, "r");
    if (!fp) {
        printf("  ℹ️  No existing records file found. Starting fresh.\n");
        record_count = 0;
        return;
    }

    record_count = 0;
    while (record_count < MAX_RECORDS &&
           fscanf(fp, " %15[^|] | %511[^\n]\n",
                  records[record_count].date,
                  records[record_count].description) == 2) {
        record_count++;
    }
    fclose(fp);
    printf("  ✅ Loaded %d maintenance record(s).\n", record_count);
}

static void save_records(void) {
    FILE *fp = fopen(FILENAME_RECORDS, "w");
    if (!fp) {
        printf("  ❌ Error: could not save records.\n");
        return;
    }
    for (int i = 0; i < record_count; i++) {
        fprintf(fp, "%s | %s\n", records[i].date, records[i].description);
    }
    fclose(fp);
}

/* ----- File I/O : Components ----- */
static void load_components(void) {
    FILE *fp = fopen(FILENAME_COMPONENTS, "r");
    if (!fp) {
        printf("  ℹ️  No components file found. Using defaults.\n");
        return;
    }

    int idx = 0;
    while (idx < component_count &&
           fscanf(fp, " %63[^|] | %d\n",
                  components[idx].name,
                  &components[idx].wear_percent) == 2) {
        idx++;
    }
    fclose(fp);
    printf("  ✅ Loaded %d component(s).\n", idx);
}

static void save_components(void) {
    FILE *fp = fopen(FILENAME_COMPONENTS, "w");
    if (!fp) {
        printf("  ❌ Error: could not save components.\n");
        return;
    }
    for (int i = 0; i < component_count; i++) {
        fprintf(fp, "%s | %d\n", components[i].name, components[i].wear_percent);
    }
    fclose(fp);
}

/* ----- Menu ----- */
static void show_menu(void) {
    printf("  ┌────────────────────────────────────┐\n");
    printf("  │  1. ➕ Add maintenance record       │\n");
    printf("  │  2. 📋 View all records            │\n");
    printf("  │  3. ⚖️  View bike weight            │\n");
    printf("  │  4. ✏️  Update bike weight          │\n");
    printf("  │  5. 🔍 View component wear         │\n");
    printf("  │  6. 🔧 Update component wear       │\n");
    printf("  │  0. 🚪 Exit                         │\n");
    printf("  └────────────────────────────────────┘\n");
}

/* ----- CRUD : Records ----- */
static void add_record(void) {
    if (record_count >= MAX_RECORDS) {
        printf("  ⚠️  Maximum records reached.\n");
        return;
    }

    MaintenanceRecord *r = &records[record_count];

    /* Auto-fill today's date */
    time_t t = time(NULL);
    struct tm *tm = localtime(&t);
    strftime(r->date, DATE_LEN, "%Y-%m-%d", tm);

    printf("  Date (auto): %s\n", r->date);
    printf("  Description: ");
    fgets(r->description, MAX_DESC_LEN, stdin);
    r->description[strcspn(r->description, "\n")] = '\0';

    record_count++;
    save_records();
    printf("  ✅ Record added successfully.\n\n");
}

static void view_records(void) {
    if (record_count == 0) {
        printf("  📭 No maintenance records yet.\n\n");
        return;
    }

    printf("  ─── Maintenance History ───\n");
    for (int i = 0; i < record_count; i++) {
        printf("  [%s] %s\n", records[i].date, records[i].description);
    }
    printf("  ───────────────────────────\n\n");
}

/* ----- CRUD : Weight ----- */
static void view_weight(void) {
    printf("  ⚖️  Current bike weight: %.2f kg\n\n", bike_weight_kg);
}

static void update_weight(void) {
    printf("  Enter new weight (kg): ");
    if (scanf("%f", &bike_weight_kg) != 1) {
        printf("  ⚠️  Invalid input.\n");
    }
    clear_input_buffer();
    printf("  ✅ Weight updated to %.2f kg.\n\n", bike_weight_kg);
}

/* ----- CRUD : Components ----- */
static void view_components(void) {
    printf("  ─── Component Wear Levels ───\n");
    for (int i = 0; i < component_count; i++) {
        printf("  %-20s [", components[i].name);
        int bars = components[i].wear_percent / 5;
        for (int j = 0; j < 20; j++) {
            if (j < bars) {
                printf("█");
            } else {
                printf("░");
            }
        }
        printf("] %3d%%", components[i].wear_percent);
        if (components[i].wear_percent >= 80) {
            printf("  ⚠️  REPLACE SOON!");
        }
        printf("\n");
    }
    printf("  ─────────────────────────────\n\n");
}

static void update_component(void) {
    printf("  Select component:\n");
    for (int i = 0; i < component_count; i++) {
        printf("    %d. %s\n", i + 1, components[i].name);
    }
    printf("  Choice: ");
    int idx;
    if (scanf("%d", &idx) != 1 || idx < 1 || idx > component_count) {
        printf("  ⚠️  Invalid component.\n");
        clear_input_buffer();
        return;
    }
    clear_input_buffer();
    idx--;

    printf("  Enter wear percentage (0-100): ");
    int wear;
    if (scanf("%d", &wear) != 1 || wear < 0 || wear > 100) {
        printf("  ⚠️  Invalid percentage.\n");
        clear_input_buffer();
        return;
    }
    clear_input_buffer();

    components[idx].wear_percent = wear;
    save_components();
    printf("  ✅ %s updated to %d%%.\n\n", components[idx].name, wear);
}
