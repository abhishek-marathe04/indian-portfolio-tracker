function savePastAttachments() {
  // 1. Paste your Google Drive folder ID between the single quotes below
  var folderId = '17OdxJWVUxcWmgv7Jx28BamS4yrtPIqcC'; 
  // var folder = DriveApp.getFolderById(folderId);

  var folder;
  try {
    folder = DriveApp.getFolderById(folderId);
  } catch(e) {
    Logger.log('ERROR: Cannot find Drive folder. Please check your Folder ID string.');
    return;
  }
  
  // 2. Define the Gmail search query for past emails with attachments
  var searchQuery = 'CDSL Consolidated Account Statement (CAS) across Mutual Funds and Depositories'; 
  
  // 3. Fetch matching email threads (Process in batches of 50 to prevent timeouts)
  var threads = GmailApp.search(searchQuery, 0, 50);
  
  for (var i = 0; i < threads.length; i++) {
    var messages = threads[i].getMessages();
    
    for (var j = 0; j < messages.length; j++) {
      var attachments = messages[j].getAttachments();
      
      for (var k = 0; k < attachments.length; k++) {
        var attachment = attachments[k];
        
        // Safety wrapper to ignore corrupted files or invalid names
        try {
          var fileName = attachment.getName();
          Logger.log(fileName)
          // Skip if the attachment has no valid name
          if (!fileName) continue; 
          
          // Prevent duplicate file creation
          var existingFiles = folder.getFilesByName(fileName);
          if (!existingFiles.hasNext()) {
            folder.createFile(attachment);
            Logger.log('Saved: ' + fileName);
          }
        } catch (e) {
          // Skips the bad file and logs the error, allowing the script to continue
          Logger.log('Skipped an invalid attachment error: ' + e.message);
        }
      }
    }
  }
  Logger.log('Batch processing complete.');
}
