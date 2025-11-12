#!/usr/bin/env python3
"""
RAPIDS Integration Module
GPU-accelerated data processing with cuDF, cuML, cuGraph

Copyright © 2025 AlphaEdge AINV
"""
import logging
from typing import Optional, Dict, Any, List, Union
import pandas as pd

logger = logging.getLogger(__name__)


class RAPIDSManager:
    """
    RAPIDS Manager
    - cuDF: GPU DataFrames (pandas on GPU)
    - cuML: GPU Machine Learning
    - cuGraph: GPU Graph Analytics
    """

    def __init__(self):
        """Initialize RAPIDS manager"""
        self.cudf_available = False
        self.cuml_available = False
        self.cugraph_available = False

        # Try importing RAPIDS libraries
        try:
            import cudf
            self.cudf = cudf
            self.cudf_available = True
            logger.info(f"✓ cuDF {cudf.__version__} available")
        except ImportError:
            logger.warning("cuDF not available. Install with: pip install cudf-cu12")

        try:
            import cuml
            self.cuml = cuml
            self.cuml_available = True
            logger.info(f"✓ cuML {cuml.__version__} available")
        except ImportError:
            logger.warning("cuML not available. Install with: pip install cuml-cu12")

        try:
            import cugraph
            self.cugraph = cugraph
            self.cugraph_available = True
            logger.info(f"✓ cuGraph {cugraph.__version__} available")
        except ImportError:
            logger.warning("cuGraph not available. Install with: pip install cugraph-cu12")

    def is_available(self) -> bool:
        """Check if any RAPIDS library is available"""
        return self.cudf_available or self.cuml_available or self.cugraph_available

    # === cuDF Functions (GPU DataFrames) ===

    def pandas_to_cudf(self, df: pd.DataFrame):
        """
        Convert pandas DataFrame to cuDF

        Args:
            df: Pandas DataFrame

        Returns:
            cuDF DataFrame
        """
        if not self.cudf_available:
            logger.warning("cuDF not available, returning pandas DataFrame")
            return df

        return self.cudf.DataFrame.from_pandas(df)

    def cudf_to_pandas(self, gdf):
        """
        Convert cuDF DataFrame to pandas

        Args:
            gdf: cuDF DataFrame

        Returns:
            Pandas DataFrame
        """
        if not self.cudf_available:
            return gdf

        return gdf.to_pandas()

    def read_csv_gpu(
        self,
        filepath: str,
        **kwargs
    ):
        """
        Read CSV on GPU (much faster than pandas)

        Args:
            filepath: Path to CSV file
            **kwargs: Additional arguments for read_csv

        Returns:
            cuDF DataFrame
        """
        if not self.cudf_available:
            logger.warning("cuDF not available, using pandas")
            return pd.read_csv(filepath, **kwargs)

        return self.cudf.read_csv(filepath, **kwargs)

    def read_parquet_gpu(
        self,
        filepath: str,
        **kwargs
    ):
        """
        Read Parquet on GPU

        Args:
            filepath: Path to Parquet file
            **kwargs: Additional arguments

        Returns:
            cuDF DataFrame
        """
        if not self.cudf_available:
            logger.warning("cuDF not available, using pandas")
            return pd.read_parquet(filepath, **kwargs)

        return self.cudf.read_parquet(filepath, **kwargs)

    def groupby_agg_gpu(
        self,
        df,
        by: Union[str, List[str]],
        agg_dict: Dict[str, Union[str, List[str]]]
    ):
        """
        GPU-accelerated groupby aggregation

        Args:
            df: DataFrame (pandas or cuDF)
            by: Column(s) to group by
            agg_dict: Aggregation dictionary

        Returns:
            Aggregated DataFrame
        """
        if self.cudf_available and not isinstance(df, self.cudf.DataFrame):
            df = self.pandas_to_cudf(df)

        result = df.groupby(by).agg(agg_dict)

        return result

    def merge_gpu(
        self,
        left,
        right,
        on: Optional[Union[str, List[str]]] = None,
        how: str = 'inner',
        **kwargs
    ):
        """
        GPU-accelerated merge (join)

        Args:
            left: Left DataFrame
            right: Right DataFrame
            on: Column(s) to join on
            how: Join type
            **kwargs: Additional arguments

        Returns:
            Merged DataFrame
        """
        if self.cudf_available:
            if not isinstance(left, self.cudf.DataFrame):
                left = self.pandas_to_cudf(left)
            if not isinstance(right, self.cudf.DataFrame):
                right = self.pandas_to_cudf(right)

            return left.merge(right, on=on, how=how, **kwargs)
        else:
            return pd.merge(left, right, on=on, how=how, **kwargs)

    # === cuML Functions (GPU Machine Learning) ===

    def kmeans_gpu(
        self,
        X,
        n_clusters: int = 8,
        max_iter: int = 300,
        random_state: int = 42
    ):
        """
        GPU-accelerated K-Means clustering

        Args:
            X: Feature matrix
            n_clusters: Number of clusters
            max_iter: Maximum iterations
            random_state: Random seed

        Returns:
            KMeans model
        """
        if not self.cuml_available:
            from sklearn.cluster import KMeans
            logger.warning("cuML not available, using sklearn")
            return KMeans(n_clusters=n_clusters, max_iter=max_iter, random_state=random_state).fit(X)

        from cuml.cluster import KMeans
        model = KMeans(n_clusters=n_clusters, max_iter=max_iter, random_state=random_state)
        model.fit(X)
        return model

    def pca_gpu(
        self,
        X,
        n_components: int = 2
    ):
        """
        GPU-accelerated PCA

        Args:
            X: Feature matrix
            n_components: Number of components

        Returns:
            PCA model
        """
        if not self.cuml_available:
            from sklearn.decomposition import PCA
            logger.warning("cuML not available, using sklearn")
            return PCA(n_components=n_components).fit(X)

        from cuml.decomposition import PCA
        model = PCA(n_components=n_components)
        model.fit(X)
        return model

    def random_forest_gpu(
        self,
        X,
        y,
        n_estimators: int = 100,
        max_depth: int = 16,
        random_state: int = 42
    ):
        """
        GPU-accelerated Random Forest

        Args:
            X: Feature matrix
            y: Labels
            n_estimators: Number of trees
            max_depth: Max tree depth
            random_state: Random seed

        Returns:
            RandomForest model
        """
        if not self.cuml_available:
            from sklearn.ensemble import RandomForestClassifier
            logger.warning("cuML not available, using sklearn")
            return RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=random_state
            ).fit(X, y)

        from cuml.ensemble import RandomForestClassifier
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state
        )
        model.fit(X, y)
        return model

    # === cuGraph Functions (GPU Graph Analytics) ===

    def pagerank_gpu(
        self,
        edge_list,
        alpha: float = 0.85,
        max_iter: int = 100
    ):
        """
        GPU-accelerated PageRank

        Args:
            edge_list: Edge list [(source, target), ...]
            alpha: Damping factor
            max_iter: Maximum iterations

        Returns:
            PageRank scores
        """
        if not self.cugraph_available:
            logger.error("cuGraph not available")
            return None

        import cudf
        import cugraph

        # Create graph
        G = cugraph.Graph()

        # Convert edge list to cuDF
        if not isinstance(edge_list, cudf.DataFrame):
            edge_df = cudf.DataFrame(edge_list, columns=['source', 'target'])
        else:
            edge_df = edge_list

        G.from_cudf_edgelist(edge_df, source='source', destination='target')

        # Compute PageRank
        pagerank_scores = cugraph.pagerank(G, alpha=alpha, max_iter=max_iter)

        return pagerank_scores

    def connected_components_gpu(
        self,
        edge_list
    ):
        """
        GPU-accelerated connected components

        Args:
            edge_list: Edge list

        Returns:
            Component labels
        """
        if not self.cugraph_available:
            logger.error("cuGraph not available")
            return None

        import cudf
        import cugraph

        G = cugraph.Graph()

        if not isinstance(edge_list, cudf.DataFrame):
            edge_df = cudf.DataFrame(edge_list, columns=['source', 'target'])
        else:
            edge_df = edge_list

        G.from_cudf_edgelist(edge_df, source='source', destination='target')

        components = cugraph.connected_components(G)

        return components


# Global manager instance
_manager: Optional[RAPIDSManager] = None


def get_manager() -> RAPIDSManager:
    """Get global RAPIDS manager"""
    global _manager
    if _manager is None:
        _manager = RAPIDSManager()
    return _manager


# Convenience functions
def to_gpu(df: pd.DataFrame):
    """Convert pandas to cuDF"""
    manager = get_manager()
    return manager.pandas_to_cudf(df)


def to_cpu(gdf):
    """Convert cuDF to pandas"""
    manager = get_manager()
    return manager.cudf_to_pandas(gdf)


def read_csv_fast(filepath: str, **kwargs):
    """Fast CSV reading on GPU"""
    manager = get_manager()
    return manager.read_csv_gpu(filepath, **kwargs)


# CLI
if __name__ == "__main__":
    import numpy as np

    print("=== RAPIDS Test ===\n")

    manager = RAPIDSManager()

    print(f"cuDF available: {manager.cudf_available}")
    print(f"cuML available: {manager.cuml_available}")
    print(f"cuGraph available: {manager.cugraph_available}")

    if manager.cudf_available:
        print("\n--- cuDF Test ---")

        # Create test DataFrame
        df = pd.DataFrame({
            'a': np.random.randn(1000),
            'b': np.random.randn(1000),
            'c': np.random.choice(['x', 'y', 'z'], 1000)
        })

        print(f"Pandas DataFrame: {df.shape}")

        # Convert to GPU
        gdf = manager.pandas_to_cudf(df)
        print(f"cuDF DataFrame: {gdf.shape}")

        # GroupBy on GPU
        result = manager.groupby_agg_gpu(gdf, by='c', agg_dict={'a': 'mean', 'b': 'sum'})
        print(f"\nGroupBy result:\n{result}")

    if manager.cuml_available:
        print("\n--- cuML Test ---")

        # Generate test data
        X = np.random.randn(1000, 10)

        # K-Means on GPU
        model = manager.kmeans_gpu(X, n_clusters=3)
        print(f"K-Means model: {model}")
        print(f"Cluster centers shape: {model.cluster_centers_.shape}")

    print("\n✓ RAPIDS test complete")
