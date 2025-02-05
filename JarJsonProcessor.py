import zipfile
from pathlib import Path
import shutil
import commentjson
from translator import do_translate_gpt

def jsonJarManager(jar_path: str, logger=None):
    """
    Processes JAR files in a directory, extracts and translates en_us.json to ko_kr.json.

    Args:
        jar_path (str): Path to the directory containing JAR files.
        logger (logging.Logger): Optional logger for recording the process.

    Returns:
        None
    """
    temp_dir = Path('./temp')
    translated_dir = Path('./translated')

    # Ensure necessary directories exist
    temp_dir.mkdir(exist_ok=True)
    translated_dir.mkdir(exist_ok=True)

    mod_path = Path(jar_path)
    mod_list = mod_path.glob('*.jar')

    for mod_file in mod_list:
        if logger:
            logger.info(f"Processing {mod_file.name}...")

        mod_temp_dir = temp_dir / mod_file.stem
        try:
            # Extract JAR file contents
            with zipfile.ZipFile(mod_file, 'r') as jar:
                jar.extractall(mod_temp_dir)
                if logger:
                    logger.info(f"Extracted {mod_file.name} to {mod_temp_dir}")

            # Locate en_us.json file
            target_json_path = next(mod_temp_dir.rglob('en_us.json'), None)
            if not target_json_path:
                if logger:
                    logger.warning(f"en_us.json not found in {mod_file.name}")
                continue

            # Translate JSON content
            translated_data = None
            with target_json_path.open('r', encoding='utf-8') as json_file:
                original_data = commentjson.load(json_file)
                json_str = commentjson.dumps(original_data, ensure_ascii=False, indent=4)
                translated_data = do_translate_gpt(target_json=json_str, logger=logger)

            # Save translated data to ko_kr.json
            ko_kr_path = target_json_path.parent / 'ko_kr.json'
            with ko_kr_path.open('w', encoding='utf-8') as json_file:
                commentjson.dump(translated_data, json_file, ensure_ascii=False, indent=4)
            if logger:
                logger.info(f"Translated JSON saved to {ko_kr_path}")

            # Recompress JAR with translated JSON
            new_jar_file = translated_dir / f"{mod_file.stem}_modified.jar"
            shutil.make_archive(new_jar_file.with_suffix(''), 'zip', mod_temp_dir)
            final_jar_file = new_jar_file.with_suffix('.jar')
            shutil.move(f"{new_jar_file.with_suffix('.zip')}", final_jar_file)

            if logger:
                logger.info(f"Translated JAR created: {final_jar_file}")

        except Exception as e:
            if logger:
                logger.error(f"An error occurred while processing {mod_file.name}: {e}")
        finally:
            # Clean up temporary files
            shutil.rmtree(mod_temp_dir, ignore_errors=True)
            if logger:
                logger.info(f"Cleaned up temporary directory: {mod_temp_dir}")

if __name__ == '__main__':
    import logging

    # Configure logger
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("jar-json-processor")

    # Run the manager
    jsonJarManager('./mod', logger=logger)
