import sys
import os
package_dir = os.path.dirname(__file__) or '.'

# Insert the package_dir_a directory at the front of the path.
sys.path.insert(0, package_dir)

bin_dir = os.path.join(package_dir, "bin")
sys.path.insert(0, bin_dir)
