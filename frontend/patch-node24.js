const path = require('path');
const patchPath = path.resolve(__dirname, 'patch-node24.js').replace(/\\/g, '/');
if (!process.env.NODE_OPTIONS || !process.env.NODE_OPTIONS.includes('patch-node24.js')) {
  process.env.NODE_OPTIONS = ((process.env.NODE_OPTIONS || '') + ` --require "${patchPath}"`).trim();
}
// On Windows with Node 24, fs.readlink on a non-symlink file returns EISDIR instead of EINVAL,
// which breaks Webpack's enhanced-resolve symlink check.
const fs = require('fs');

const origReadlink = fs.readlink;
fs.readlink = function (path, options, callback) {
  if (typeof options === 'function') {
    callback = options;
    options = {};
  }
  return origReadlink.call(fs, path, options, (err, linkString) => {
    if (err && (err.code === 'EISDIR' || err.code === 'UNKNOWN')) {
      err.code = 'EINVAL';
    }
    if (callback) callback(err, linkString);
  });
};

const origReadlinkSync = fs.readlinkSync;
fs.readlinkSync = function (path, options) {
  try {
    return origReadlinkSync.call(fs, path, options);
  } catch (err) {
    if (err && (err.code === 'EISDIR' || err.code === 'UNKNOWN')) {
      err.code = 'EINVAL';
    }
    throw err;
  }
};

if (fs.promises && fs.promises.readlink) {
  const origPromisesReadlink = fs.promises.readlink;
  fs.promises.readlink = async function (path, options) {
    try {
      return await origPromisesReadlink.call(fs.promises, path, options);
    } catch (err) {
      if (err && (err.code === 'EISDIR' || err.code === 'UNKNOWN')) {
        err.code = 'EINVAL';
      }
      throw err;
    }
  };
}
