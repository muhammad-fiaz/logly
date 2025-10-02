use pyo3::Bound;
use pyo3::types::{PyAnyMethods, PyDict, PyDictMethods};

/// Convert a Python dictionary to a vector of key-value string pairs.
///
/// This function extracts string representations of keys and values from a
/// Python dictionary, handling various Python types gracefully.
///
/// # Arguments
///
/// * `dict` - The Python dictionary to convert
///
/// # Returns
///
/// A vector of (key, value) string pairs
pub fn dict_to_pairs(dict: &Bound<'_, PyDict>) -> Vec<(String, String)> {
    let mut out = Vec::new();
    for (k, v) in dict.iter() {
        let k_str = k.extract::<String>().unwrap_or_else(|_| "".to_string());
        let v_str = match v.str() {
            Ok(s) => s.extract::<String>().unwrap_or_else(|_| "".to_string()),
            Err(_) => "".to_string(),
        };
        out.push((k_str, v_str));
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use pyo3::prelude::*;
    use pyo3::types::PyDict;

    #[test]
    fn test_dict_to_pairs_empty() -> pyo3::PyResult<()> {
        Python::initialize();
        Python::attach(|py| {
            let dict = PyDict::new(py);
            let pairs = dict_to_pairs(&dict);
            assert_eq!(pairs.len(), 0);
            Ok(())
        })
    }

    #[test]
    fn test_dict_to_pairs_string_values() -> pyo3::PyResult<()> {
        Python::initialize();
        Python::attach(|py| {
            let dict = PyDict::new(py);
            dict.set_item("key1", "value1")?;
            dict.set_item("key2", "value2")?;

            let pairs = dict_to_pairs(&dict);
            assert_eq!(pairs.len(), 2);

            let mut found_key1 = false;
            let mut found_key2 = false;
            for (k, v) in pairs {
                match k.as_str() {
                    "key1" => {
                        assert_eq!(v, "value1");
                        found_key1 = true;
                    }
                    "key2" => {
                        assert_eq!(v, "value2");
                        found_key2 = true;
                    }
                    _ => panic!("Unexpected key: {}", k),
                }
            }
            assert!(found_key1 && found_key2);
            Ok(())
        })
    }

    #[test]
    fn test_dict_to_pairs_mixed_types() -> pyo3::PyResult<()> {
        Python::initialize();
        Python::attach(|py| {
            let dict = PyDict::new(py);
            dict.set_item("string", "text")?;
            dict.set_item("number", 42)?;
            dict.set_item("boolean", true)?;

            let pairs = dict_to_pairs(&dict);
            assert_eq!(pairs.len(), 3);

            let mut found_string = false;
            let mut found_number = false;
            let mut found_boolean = false;
            for (k, v) in pairs {
                match k.as_str() {
                    "string" => {
                        assert_eq!(v, "text");
                        found_string = true;
                    }
                    "number" => {
                        assert_eq!(v, "42");
                        found_number = true;
                    }
                    "boolean" => {
                        assert_eq!(v, "True");
                        found_boolean = true;
                    }
                    _ => panic!("Unexpected key: {}", k),
                }
            }
            assert!(found_string && found_number && found_boolean);
            Ok(())
        })
    }

    #[test]
    fn test_dict_to_pairs_non_string_keys() -> pyo3::PyResult<()> {
        Python::initialize();
        Python::attach(|py| {
            let dict = PyDict::new(py);
            dict.set_item(123, "value")?;
            dict.set_item(true, "bool_value")?;

            let pairs = dict_to_pairs(&dict);
            assert_eq!(pairs.len(), 2);

            // Non-string keys should be converted to empty strings
            for (k, v) in pairs {
                assert_eq!(k, "");
                assert!(!v.is_empty());
            }
            Ok(())
        })
    }
}
