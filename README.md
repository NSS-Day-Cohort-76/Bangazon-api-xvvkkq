# Bangazon Platform API
  <span>Bangazon is an e-commerce platform where users can interact as customers or sellers </span>


## Overview
### Customers can:
* View all products posted for sale
* Filter products by minimum price, location, category, and number sold of product
* Rate and review a product
* Like a product
* Recommend a product to another user
* Add a product to their cart
* Complete or delete the order in their cart

### Sellers can:
* Choose to create a store
* Edit a product listed in their store
* Delete a product listed in their store

This is the Server-Side of the application. The Client-Side of the application can be found [here](https://github.com/NSS-Day-Cohort-76/Bangazon-client-xvvkkq)

## System Dependencies

1. Follow installation guide for installing [pipx](https://pipx.pypa.io/stable/installation/).
2. Run `pipx install poetry`.
3. Run the command below for your operating system.

### Mac OS

```sh
brew install libtiff libjpeg webp little-cms2
```

### Linux

```sh
sudo apt install libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev
```

## Setup

1. Clone this repository and change to the directory in the terminal.
2. Run `poetry env activate` and wait for the virtual environment to be created.
3. Run `poetry install` to install dependencies.
4. Run `pip install setuptools`
5. Run migrations and install starter data with the `./seed_data.sh` script.
6. Open the project in VS Code if you haven't yet.
7. Ensure that the correct Python Interpreter is chosen in VS Code.
8. Start your debugger.

## Postman Request Collection

1. Open the [Yaak](https://yaak.app/) API client
2. Click **Import**
3. Click **Select File**
4. Open the **`api-requests-collection.json`** file that is in this project.
5. Click **Import** to complete the process
6. You will see a confirmation that a new workspace has been created for you.

#### Test Login Request

1. Expand the **Profile** collection
2. Click on **Login** to open the request
3. Send the request.
4. You should get a response back that looks like this
   ```json
   {
       "valid": true,
       "token": "9ba45f09651c5b0c404f37a2d2572c026c146690",
       "id": 5
   }
   ```

## User Authentication

Look in the `users.json` file for the usernames. While the passwords in the fixture are encrypted, the source password for every user is `Admin8*`

## Changing Your Database

You can run the `./seed-data.sh` script any time to make changes to database models, or just want to roll back your data to its original state. It deletes the database, any existing migrations, and then re-creates the database based on your current models, and inserts starter data.


## Contributors
<a href="https://github.com/dwest1220">
  <img src="https://avatars.githubusercontent.com/u/196469455?v=4" height="50" width="50">
</a>
<a href="https://github.com/kaseyendsley">
  <img src="https://avatars.githubusercontent.com/u/194643988?v=4" height="50" width="50">
</a>
<a href="https://github.com/britttttt">
  <img src="https://avatars.githubusercontent.com/u/51220225?v=4" height="50" width="50">
</a>
<a href="https://github.com/TylerMartin713">
  <img src="https://avatars.githubusercontent.com/u/156736886?v=4" height="50" width="50">


Made with JavaScript, React, Next.JS, Bulma, Python, and Django rest API's in [Nashville Software School's](https://nashvillesoftwareschool.com/) Full-Stack Software Developer Program (Cohort-76)