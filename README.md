# du2html - by CrooLyyCheck and AI
du2html is a Python script that converts the output of the du (disk usage) command into an interactive, browser-viewable HTML file displaying the directory tree with sizes. The visualization uses Bootstrap 5 for styling and features lazy loading of subtrees to ensure fast page load and smooth navigation even for very large directory structures.

Features
Parses du output files where each line contains size and path separated by a tab (\t), e.g.:

4.0K	/mnt/disk1/4k.file
8.0K	/mnt/disk1/some/awesone/files/pictures
Ignores garbage lines such as status messages (nohup: ignoring input).

Builds a nested directory tree with size information.

Renders the tree as an interactive, collapsible HTML page using Bootstrap 5.

Implements lazy loading of subfolders: initially loads only the top-level nodes, subtrees are generated dynamically when expanding folders. This avoids slow page loads for large trees.

Clean, modern, responsive UI that works well on desktop and mobile browsers.

Requirements
Python 3.6 or newer

Internet access for Bootstrap 5 assets (loaded from CDN)

Usage
Run du on your system and save output to a file (this make to run in backgroud, you can even close connection to terminal and process don't be closed. Check with btop or htop command this process is still running, or monit output file size):

nohup du -h /mnt/mydataset --max-depth=10 > ./du-output-$(date +%Y-%m-%d).txt 2>&1 &

(Make sure the max-depth and path are set to your needs. Adjust command as needed.)

Run the script:

python du2html.py du-output.txt output.html
Open output.html in a modern web browser (Chrome, Firefox, Edge, Safari).

Click the + button next to any folder to expand and explore its subdirectories.

Installation
Simply download or clone the script du2html.py. No external Python libraries needed beyond the standard library.

How it works
The script reads the provided du output file.

It builds an in-memory nested dictionary representing the directory tree.

Outputs a standalone HTML file embedding the entire tree as JSON.

The initial HTML shows only the root level.

JavaScript code lazily renders subtrees on demand when user expands folders, making UI responsive even with huge data.

This project is open source and available under the MIT License.

Contributing
Feel free to submit issues or pull requests for improvements, bug fixes, or new features!

Contact
For questions or feedback, please open an issue on GitHub or contact the maintainer.
