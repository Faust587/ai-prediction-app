const fs = require('fs');
const path = require('path');

const directoryToScan = '.'; // Заміни на свою папку
const outputFile = './output.txt';         // Файл, куди буде записано результат

// Рекурсивна функція для збору всіх файлів
function getAllFiles(dirPath, filesList = []) {
  const items = fs.readdirSync(dirPath);
  for (const item of items) {
    const fullPath = path.join(dirPath, item);
    const stat = fs.statSync(fullPath);
    if (stat.isDirectory()) {
      getAllFiles(fullPath, filesList);
    } else {
      filesList.push(fullPath);
    }
  }
  return filesList;
}

// Генеруємо вміст
function generateFormattedContent(files) {
  let result = '';
  for (const file of files) {
    const ext = path.extname(file);
    const baseName = path.basename(file);
    try {
      const content = fs.readFileSync(file, 'utf-8');
      result += `${baseName}\n\n${content}\n\n`;
    } catch (err) {
      console.error(`Помилка читання файлу: ${file}`, err);
    }
  }
  return result;
}

// Основна функція
function run() {
  const allFiles = getAllFiles(directoryToScan);
  const outputContent = generateFormattedContent(allFiles);
  fs.writeFileSync(outputFile, outputContent, 'utf-8');
  console.log(`✅ Готово! Результат збережено у ${outputFile}`);
}

run();