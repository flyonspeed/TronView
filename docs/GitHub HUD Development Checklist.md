**Git Workflow Checklist for \`flyonspeed/TronView\`: HUD SW Development**

								**(22Aug 24\)**

### **Git Workflow Checklist with Detailed Examples**

#### **1\. Configure Your Git Identity (Only Required Once per Machine or Repository)**

* **Globally (Applies to All Repositories):**

**Set your email and name for all repositories on your machine:**  
**Copy code**  
**`git config user.email "jane.doe@example.com"`**

**`git config user.name "Jane Doe"`**

* **Example: If your name is Jane Doe and your email is jane.doe@example.com, this command will ensure that all your commits on this machine are associated with this identity.**  
* **Locally (Applies Only to the Current Repository):**

**If you want to use a different identity just for this project:**  
**Copy code**  
**`git config user.email "john.doe@example.com"`**

**`git config user.name "John Doe"`**

* **Example: If you’re working on a specific project under a different name or email, these commands will apply only to the repository you're in.**

#### **2\. Clone the Repository**

* **Open your terminal.**  
* **Navigate to the directory where you want to clone the repository.**

**Example: If you want to clone the repository to a folder named `Projects` in your home directory, navigate there:**  
**Copy code**  
**`cd ~/Projects`**

**Run the clone command:**  
**Copy code**  
**`git clone https://github.com/flyonspeed/TronView.git`**

* **This command will download the repository from GitHub to your local machine, creating a new folder named `TronView` in your current directory.**

#### **3\. Navigate to the Project Directory**

**Change to the directory of the cloned repository:**

**Copy code**  
**`cd TronView`**

* **Example: After cloning, navigate into the `TronView` directory to start working on the project files.**

#### **4\. Check Out a New Branch**

**Create and switch to a new branch for your feature or bug fix:**  
**Copy code**  
**`git checkout -b feature/add-login`**

* **Example: This command creates a new branch named `feature/add-login` and switches to it. Use a branch name that clearly describes the work you’re doing, such as `bugfix/fix-typo` or `feature/add-dark-mode`.**

#### **5\. Pull the Latest Changes (Optional)**

**Ensure you have the latest changes from the remote repository:**  
**Copy code**  
**`git pull origin main`**

* **Example: This command pulls the latest changes from the `main` branch of the remote repository. If other team members have pushed updates, this command ensures your branch is up-to-date with their changes.**

#### **6\. Work on the Code**

* **Edit files, add new files, or delete files as needed.**

  **Example: Open `hud.py` in your text editor or IDE, make your changes, and save the file. You might add a new function or fix a bug in this step.**

#### **7\. Stage Your Changes**

**Stage specific changes for the commit:**  
**Copy code**  
**`git add hud.py`**

* **Example: This command stages the changes made to `hud.py` for the next commit. Only the changes in this file will be included in the commit.**

**Stage all changes:**  
**Copy code**  
**`git add .`**

* **Example: This command stages all modified files in the current directory and subdirectories. Use this if you’ve made changes to multiple files and want to include them all in the commit.**

#### **8\. Commit Your Changes with a Descriptive Message**

**Commit your staged changes:**  
**Copy code**  
**`git commit -m "Fix flickering issue in HUD display"`**

* **Example: This commit message explains what the commit does. It’s concise and descriptive, helping others understand what was changed without needing to look at the code.**

**Another example for adding a feature:**  
**Copy code**  
**`git commit -m "Add support for new altitude sensor in HUD"`**

* **Example: This message indicates that the commit includes code that adds support for a new sensor.**

#### **9\. Push Your Branch to GitHub**

**Push your branch to the remote repository:**  
**Copy code**  
**`git push origin feature/add-login`**

* **Example: This command uploads your local branch (`feature/add-login`) to the remote GitHub repository so that others can see and review your work.**

#### **10\. Create a Pull Request (PR)**

* **Go to the `flyonspeed/TronView` repository on GitHub in your browser.**  
* **Create a Pull Request for your branch:**  
  * **Example: On GitHub, you’ll see an option to compare your branch (`feature/add-login`) with the `main` branch and create a PR.**  
* **Fill out the PR form:**  
  * **Add a clear title and description for your PR.**  
  * **Example: Title: `Add Login Feature`, Description: `This PR adds a login feature with username and password validation.`**  
* **Assign reviewers and set labels if necessary.**

#### **11\. Wait for Review**

* **Wait for feedback from your reviewers.**  
  * **Example: Reviewers might comment on your code, suggest changes, or approve the PR. Address any feedback as needed.**

#### **12\. Make Revisions (if needed)**

* **If changes are requested, make the revisions in your branch.**

**Commit and push the changes:**  
**Copy code**  
**`git commit -m "Refactor login validation logic"`**

**`git push origin feature/add-login`**

*   
  * **Example: This updates your PR with the new changes based on reviewer feedback.**

#### **13\. Merge the Pull Request (if approved)**

* **Once your PR is approved, you or the repository maintainer can merge it into the main branch.**  
* **If there are no conflicts, use the “Merge” button in the PR interface on GitHub.**  
  * **Example: After merging, your changes are now part of the main branch and available to everyone.**

#### **14\. Delete the Feature Branch (Optional)**

**Delete the branch locally:**  
**Copy code**  
**`git branch -d feature/add-login`**

* **Example: This command deletes the local branch `feature/add-login` since it has been merged.**

**Delete the branch on GitHub:**  
**Copy code**  
**`git push origin --delete feature/add-login`**

* **Example: This command deletes the branch from the remote repository on GitHub.**

#### **15\. Sync with the Main Branch**

**After your PR is merged, switch back to the main branch:**  
**Copy code**  
**`git checkout main`**

* **Pull the latest changes:**  
  **Copy code**  
  **`git pull origin main`**  
* **Example: This ensures your local `main` branch is up-to-date with the latest changes from the remote repository.**

**This checklist now includes detailed examples for each step, helping guide you through the entire Git workflow process.** 