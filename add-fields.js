const accessToken = require('../lib/access-token').getAccessToken;
const firebase = require('firebase');
const { db } = require('../lib/firebase-config');
const semver = require('semver');

const modFields = async () => {
  // sign in
  const AUTH_TOKEN = accessToken();
  await firebase.auth().signInWithCustomToken(AUTH_TOKEN.token);

  // get all the companies
  const companies = await db.collection('companies').get();

  // get all the projects for the companies
  const projectPromises = [];
  companies.forEach(co => {
    console.log('Company:', co.get('displayName'));

    // fetch all the projects, returns Promises
    projectPromises.push(
      db.collection('companies').doc(co.id).collection('projects').get()
    );
  });

  // wait until all the promises for the fetching the projects have resolved
  const projects = await Promise.all(projectPromises);

  // get all the assets for the projects
  const assetProms = [];
  projects.forEach(p => {
    p.forEach(prj => {
      // fetch all the assets, returns Promises
      assetProms.push(prj.ref.collection('assets').get());
    });
  });

  // wait until all the promises for the fetching the assets have resolved
  const assets = await Promise.all(assetProms);

  // get all the assets
  const updatePromises = [];
  assets.forEach(a => {
    a.forEach(asset => {
      // get the asset version
      console.log(asset.data().path);

      const version = asset.get('version');

      // Update the document by merging in the new fields
      updatePromises.push(
        asset.ref.set({
          version_major: semver.major(version),
          version_minor: semver.minor(version),
          version_patch: semver.patch(version),
          version_metadata: '',
          version_pre_release: semver.prerelease(version) || ''
        }, { merge: true })
      );
    });
  });

  // wait until all the promises for the updates have resolved
  await Promise.all(updatePromises);


  process.exit();
};

modFields();
