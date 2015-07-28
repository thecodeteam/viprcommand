import sys
import os
base_dir = os.path.dirname(__file__) or '.'
print('Base directory:' + base_dir)

# Insert the package_dir_a directory at the front of the path.
package_dir = os.path.join(base_dir)
sys.path.insert(0, package_dir)

bin_dir = os.path.join(package_dir, "bin")
sys.path.insert(0, bin_dir)
