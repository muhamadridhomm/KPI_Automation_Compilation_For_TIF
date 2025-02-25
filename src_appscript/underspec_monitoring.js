/**
 * Clears the destination sheet and copies data from the source sheet to the destination sheet.
 * Deletes column B in the destination sheet after copying.
 */
function clearAndCopy() {
  var sourceSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('SEMESTA H-0');
  var destinationSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('SEMESTA H-1');
  
  // Clear existing data in the destination sheet
  destinationSheet.clear();
  
  // Get the data range from the source sheet
  var sourceDataRange = sourceSheet.getDataRange();
  
  // Get the values from the source sheet
  var sourceValues = sourceDataRange.getValues();
  
  // Define the range in the destination sheet to paste the data
  var destinationRange = destinationSheet.getRange(1, 1, sourceValues.length, sourceValues[0].length);
  
  // Paste the values into the destination sheet
  destinationRange.setValues(sourceValues);
  
  // Delete column B in the destination sheet
  destinationSheet.deleteColumn(2); // Column B
}

/**
 * Copies data from the 'DASH' sheet to the 'HISTORI DSH BARU' sheet.
 * If the target sheet does not exist, it creates it.
 */
function copyDash() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sourceSheet = ss.getSheetByName('DASH');  // Source sheet
  var targetSheet = ss.getSheetByName('HISTORI DSH BARU');  // Target sheet
  
  // Create the target sheet if it doesn't exist
  if (!targetSheet) {
    targetSheet = ss.insertSheet('HISTORI DSH BARU');
  }

  // Get the source range and values
  var sourceRange = sourceSheet.getRange('A1:T29');
  var sourceValues = sourceRange.getValues();
  
  // Find the last row in the target sheet
  var lastRow = targetSheet.getLastRow();
  
  // Determine the new row to paste data (2 rows below the last filled row)
  var newRow = lastRow + 2;
  
  // Copy the range to the target sheet
  sourceRange.copyTo(targetSheet.getRange(newRow, 1));
  targetSheet.getRange(newRow, 1, sourceValues.length, sourceValues[0].length).setValues(sourceValues);
}

/**
 * Copies values from specific ranges in the 'DETAIL NOMOR' sheet.
 */
function detailNomorShift1() {
  var spreadsheet = SpreadsheetApp.getActive();
  var sourceSheet = spreadsheet.getSheetByName('DETAIL NOMOR');
  
  // Copy values from B3:G1502 to A3
  sourceSheet.getRange('B3:G1502').copyTo(sourceSheet.getRange('A3'), SpreadsheetApp.CopyPasteType.PASTE_VALUES, false);
  
  // Copy values from I3:I1502 to G3
  sourceSheet.getRange('I3:I1502').copyTo(sourceSheet.getRange('G3'), SpreadsheetApp.CopyPasteType.PASTE_VALUES, false);
}

/**
 * Copies data from the 'DATA COPYAN' sheet to the 'HISTORI DATA' sheet.
 */
function copyDataHistori() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sourceSheet = ss.getSheetByName('DATA COPYAN');
  var targetSheet = ss.getSheetByName('HISTORI DATA');
  
  // Get the range from the second row to the last filled row in the source sheet
  var sourceRange = sourceSheet.getRange(2, 1, sourceSheet.getLastRow() - 1, sourceSheet.getLastColumn());
  var data = sourceRange.getValues();
  
  // Find the last empty row in the target sheet
  var targetLastRow = targetSheet.getLastRow() + 1;

  // Paste the values into the target sheet
  targetSheet.getRange(targetLastRow, 1, data.length, data[0].length).setValues(data);
}

/**
 * Updates the file link in the 'DATA COPYAN' sheet with a formula to import data from a specific file.
 */
function updateFileLink() {
  var fileName = 'Data Unspec AQI.xlsx'; // File name
  var folderId = '1rEwGZq2bsfgi9XEtsIt9YbhRjXiwmrxX'; // Folder ID
  
  // Get the folder
  var folder = DriveApp.getFolderById(folderId);
  
  // Search for the file by name in the specified folder
  var files = folder.getFilesByName(fileName);
  
  if (files.hasNext()) {
    var file = files.next();
    var fileId = file.getId();
    var fileUrl = 'https://docs.google.com/spreadsheets/d/' + fileId + '/edit';
    var cellformula = '=IMPORTRANGE("'+ fileUrl + '","Data Unspec AQI.xlsx!A5:V1000")';

    // Update cell A2 of the 'DATA COPYAN' sheet with the formula
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("DATA COPYAN");
    var cellToUpdate = 'A2'; // Cell to update
    sheet.getRange(cellToUpdate).setValue(cellformula);

    Logger.log('File link updated to: ' + cellformula);
  } else {
    Logger.log('File not found.');
  }
}

/**
 * Executes a series of functions to prepare the spreadsheet for a new day.
 */
function ClearNewDay() {
  copyDash();
  detailNomorShift1();
  clearAndCopy();
  copyDataHistori();
}
