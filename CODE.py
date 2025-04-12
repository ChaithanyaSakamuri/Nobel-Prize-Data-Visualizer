import os
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from tkinter import Tk, Label, StringVar, Toplevel, Text, Scrollbar, messagebox
from tkinter import ttk
from PIL import Image, ImageTk  

#Ensure correct dataset path
csv_file_path = r"nobel.csv"

if not os.path.exists(csv_file_path):
    print(f"Error: CSV file not found at {csv_file_path}")
    exit()

#Load dataset
data = pd.read_csv(csv_file_path)

#Column Name Adjustments
expected_columns = ['birth_country', 'year', 'sex', 'category', 'birth_date', 'full_name', 
                    'birth_city', 'motivation', 'organization_country']

for col in expected_columns:
    if col not in data.columns:
        print(f"Warning: Column '{col}' is missing from dataset!")
        data[col] = np.nan

#Data Preparation
sns.set(style="whitegrid", palette="muted")

data['usa_born_winner'] = data['birth_country'] == 'United States of America'
data['decade'] = (np.floor(data['year'] / 10) * 10).astype('Int64')

prop_usa_winners = data.groupby('decade', as_index=False)['usa_born_winner'].mean()

data['female_winner'] = data['sex'] == 'Female'
prop_female_winners = data.groupby(['decade', 'category'], as_index=False)['female_winner'].mean()

#Properly parse birth_date and compute age
data['birth_date'] = pd.to_datetime(data['birth_date'], errors='coerce')
data['age'] = data['year'] - data['birth_date'].dt.year
data = data[(data['age'].notna()) & (data['year'].notna()) & (data['age'] > 0)]

country_counts = data['organization_country'].value_counts()
top_10_countries = country_counts.head(10)
others_count = country_counts.iloc[10:].sum()
country_counts_filtered = pd.concat([top_10_countries, pd.Series({'Others': others_count})])

#Function to display plots
def show_plot(choice):
    plt.figure(figsize=(10, 6))
    
    if choice == "Proportion of USA-born Winners":
        sns.lineplot(data=prop_usa_winners, x='decade', y='usa_born_winner', color="darkblue", linewidth=2.5)
        plt.title("Proportion of USA-born Nobel Prize Winners per Decade", fontsize=16, color="darkblue")
        plt.xlabel("Decade", fontsize=12, color="navy")
        plt.ylabel("Proportion", fontsize=12, color="navy")

    elif choice == "Proportion of Female Winners":
        sns.lineplot(data=prop_female_winners, x='decade', y='female_winner', hue='category', palette="Set2")
        plt.title("Proportion of Female Nobel Prize Winners per Decade by Category", fontsize=16, color="darkblue")
        plt.xlabel("Decade", fontsize=12, color="navy")
        plt.ylabel("Proportion", fontsize=12, color="navy")
        plt.legend(title="Category")

    elif choice == "Age of Winners Over Time":
        filtered_data = data[pd.to_numeric(data['age'], errors='coerce').notna()]
        sns.regplot(data=filtered_data, x="year", y="age", lowess=True, scatter_kws={'s': 10}, line_kws={'color': 'black'})
        plt.title("Age of Nobel Prize Winners Over Time", fontsize=16, color="darkblue")
        plt.xlabel("Year", fontsize=12, color="navy")
        plt.ylabel("Age", fontsize=12, color="navy")

    elif choice == "Top 10 Countries":
        top_10_countries.plot(kind='bar', color='mediumseagreen')
        plt.title("Top 10 Countries by Nobel Prizes", fontsize=16, color="darkblue")
        plt.xlabel("Country", fontsize=12, color="navy")
        plt.ylabel("Number of Prizes", fontsize=12, color="navy")

    elif choice == "Country Distribution (Pie Chart)":
        plt.pie(
            country_counts_filtered,
            labels=country_counts_filtered.index,
            autopct='%1.1f%%',
            startangle=140,
            colors=sns.color_palette("pastel"),
            textprops={'fontsize': 8},
        )
        plt.title('Distribution of Nobel Prize Affiliations by Country', fontsize=16, color="darkblue")
        plt.axis('equal')

    else:
        messagebox.showerror("Error", "Invalid plot selection!")
        return

    plt.tight_layout()
    plt.show()

#Function to search laureates
def search_laureate():
    person_name = entry_name.get().strip().lower()
    
    if 'full_name' not in data.columns:
        messagebox.showerror("Error", "Column 'full_name' is missing in dataset!")
        return
    
    matching_laureates = data[data['full_name'].str.lower().str.contains(person_name, na=False)]
    
    if not matching_laureates.empty:
        laureate_info_window = Toplevel(root)
        laureate_info_window.title("Laureate Information")
        laureate_info_window.geometry("600x400")

        scrollbar = Scrollbar(laureate_info_window)
        scrollbar.pack(side="right", fill="y")

        text_area = Text(laureate_info_window, wrap="word", yscrollcommand=scrollbar.set)
        text_area.pack(expand=True, fill="both")
        scrollbar.config(command=text_area.yview)

        for _, laureate in matching_laureates.iterrows():
            info = (
                f"Name: {laureate['full_name']}\n"
                f"Place of Birth: {laureate['birth_city']}\n"
                f"Date of Birth: {laureate['birth_date'].date() if pd.notna(laureate['birth_date']) else 'Unknown'}\n"
                f"Age: {int(laureate['age']) if pd.notna(laureate['age']) else 'Unknown'}\n"
                f"Motivation: {laureate['motivation']}\n"
                f"Award Year: {laureate['year']}\n"
                f"Category: {laureate['category']}\n\n"
            )
            text_area.insert("end", info)
    else:
        messagebox.showinfo("No Results", f"No information found for laureate: {person_name}")

#Function to display image
def display_image_at_top():
    image_path = r"nobelpic.jpg"
    if not os.path.exists(image_path):
        return

    image = Image.open(image_path).resize((200, 200))
    photo = ImageTk.PhotoImage(image)

    image_label = Label(root, image=photo)
    image_label.image = photo  
    image_label.pack(pady=10)

#Initialize GUI
root = Tk()
root.title("Nobel Prize Analysis")
root.geometry("450x500")

display_image_at_top()

Label(root, text="Enter Laureate Name:").pack(pady=5)
entry_name = StringVar()
entry_box = ttk.Entry(root, textvariable=entry_name, width=30)
entry_box.pack(pady=5)
ttk.Button(root, text="Search Laureate", command=search_laureate).pack(pady=5)

Label(root, text="Select Plot:").pack(pady=5)
plot_choice = StringVar(value="Proportion of USA-born Winners")
plot_menu = ttk.OptionMenu(root, plot_choice, *["Proportion of USA-born Winners", "Proportion of Female Winners", "Age of Winners Over Time", "Top 10 Countries", "Country Distribution (Pie Chart)"])
plot_menu.pack(pady=5)

ttk.Button(root, text="Show Plot", command=lambda: show_plot(plot_choice.get())).pack(pady=5)

root.mainloop()
