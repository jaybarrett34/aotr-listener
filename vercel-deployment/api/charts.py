"""
Chart Generation using QuickChart API

Generates chart images for Discord embeds showing AOTR statistics.
"""

import json
from urllib.parse import quote
from typing import Dict, List


def generate_quickchart_url(chart_config: Dict) -> str:
    """
    Generate a QuickChart URL from a Chart.js config.

    Args:
        chart_config: Chart.js configuration dict

    Returns:
        URL to the generated chart image
    """
    # QuickChart API endpoint
    base_url = 'https://quickchart.io/chart'

    # Convert config to JSON and URL encode
    config_json = json.dumps(chart_config)
    encoded_config = quote(config_json)

    return f'{base_url}?c={encoded_config}'


def create_drops_bar_chart(drops_summary: Dict[str, int]) -> str:
    """
    Create a bar chart showing drop type distribution.

    Colors: Common=gray, Rare=blue, Epic=purple, Legendary=gold, Mythic=red
    """
    # Define order and colors
    rarity_order = ['common', 'rare', 'epic', 'legendary', 'mythic']
    rarity_colors = {
        'common': 'rgba(128, 128, 128, 0.8)',      # Gray
        'rare': 'rgba(59, 130, 246, 0.8)',         # Blue
        'epic': 'rgba(168, 85, 247, 0.8)',         # Purple
        'legendary': 'rgba(250, 204, 21, 0.8)',    # Gold
        'mythic': 'rgba(239, 68, 68, 0.8)'         # Red
    }

    # Prepare data in order
    labels = []
    data = []
    colors = []

    for rarity in rarity_order:
        if rarity in drops_summary and drops_summary[rarity] > 0:
            labels.append(rarity.capitalize())
            data.append(drops_summary[rarity])
            colors.append(rarity_colors[rarity])

    # If no data, show empty chart
    if not labels:
        labels = ['No Drops Yet']
        data = [0]
        colors = ['rgba(128, 128, 128, 0.3)']

    chart_config = {
        'type': 'bar',
        'data': {
            'labels': labels,
            'datasets': [{
                'label': 'Total Drops',
                'data': data,
                'backgroundColor': colors
            }]
        },
        'options': {
            'title': {
                'display': True,
                'text': 'All-Time Drops Distribution',
                'fontSize': 16,
                'fontColor': '#ffffff'
            },
            'legend': {
                'display': False
            },
            'scales': {
                'yAxes': [{
                    'ticks': {
                        'beginAtZero': True,
                        'fontColor': '#ffffff',
                        'precision': 0
                    },
                    'gridLines': {
                        'color': 'rgba(255, 255, 255, 0.1)'
                    }
                }],
                'xAxes': [{
                    'ticks': {
                        'fontColor': '#ffffff'
                    },
                    'gridLines': {
                        'color': 'rgba(255, 255, 255, 0.1)'
                    }
                }]
            },
            'plugins': {
                'datalabels': {
                    'anchor': 'end',
                    'align': 'top',
                    'color': '#ffffff',
                    'font': {
                        'weight': 'bold'
                    }
                }
            }
        }
    }

    # Set background color for dark theme
    chart_config['options']['layout'] = {
        'padding': 20
    }
    chart_config['backgroundColor'] = '#2b2d31'

    return generate_quickchart_url(chart_config)


def create_special_rewards_bar_chart(special_summary: Dict[str, int]) -> str:
    """Create a bar chart showing special rewards distribution."""
    if not special_summary:
        # Empty chart
        labels = ['No Special Rewards Yet']
        data = [0]
        colors = ['rgba(128, 128, 128, 0.3)']
    else:
        labels = list(special_summary.keys())
        data = list(special_summary.values())
        # Use rainbow colors for special rewards
        colors = [
            'rgba(239, 68, 68, 0.8)',   # Red
            'rgba(249, 115, 22, 0.8)',  # Orange
            'rgba(250, 204, 21, 0.8)',  # Yellow
            'rgba(34, 197, 94, 0.8)',   # Green
            'rgba(59, 130, 246, 0.8)',  # Blue
            'rgba(168, 85, 247, 0.8)',  # Purple
            'rgba(236, 72, 153, 0.8)'   # Pink
        ]
        # Cycle colors if more rewards than colors
        colors = colors * (len(labels) // len(colors) + 1)
        colors = colors[:len(labels)]

    chart_config = {
        'type': 'bar',
        'data': {
            'labels': labels,
            'datasets': [{
                'label': 'Total Count',
                'data': data,
                'backgroundColor': colors
            }]
        },
        'options': {
            'title': {
                'display': True,
                'text': 'All-Time Special Rewards',
                'fontSize': 16,
                'fontColor': '#ffffff'
            },
            'legend': {
                'display': False
            },
            'scales': {
                'yAxes': [{
                    'ticks': {
                        'beginAtZero': True,
                        'fontColor': '#ffffff',
                        'precision': 0
                    },
                    'gridLines': {
                        'color': 'rgba(255, 255, 255, 0.1)'
                    }
                }],
                'xAxes': [{
                    'ticks': {
                        'fontColor': '#ffffff',
                        'maxRotation': 45,
                        'minRotation': 45
                    },
                    'gridLines': {
                        'color': 'rgba(255, 255, 255, 0.1)'
                    }
                }]
            },
            'plugins': {
                'datalabels': {
                    'anchor': 'end',
                    'align': 'top',
                    'color': '#ffffff',
                    'font': {
                        'weight': 'bold'
                    }
                }
            }
        }
    }

    chart_config['options']['layout'] = {'padding': 20}
    chart_config['backgroundColor'] = '#2b2d31'

    return generate_quickchart_url(chart_config)


def create_time_line_chart(runs: List[Dict]) -> str:
    """Create a line chart showing average completion time over runs."""
    if not runs:
        # Empty chart
        labels = ['No Data']
        data = [0]
    else:
        labels = [f"Run {i+1}" for i in range(len(runs))]
        # Convert to minutes, handle None values as 0
        data = [(run['time_seconds'] or 0) / 60 for run in runs]

    chart_config = {
        'type': 'line',
        'data': {
            'labels': labels,
            'datasets': [{
                'label': 'Time (minutes)',
                'data': data,
                'borderColor': 'rgba(59, 130, 246, 1)',
                'backgroundColor': 'rgba(59, 130, 246, 0.2)',
                'fill': True,
                'tension': 0.4
            }]
        },
        'options': {
            'title': {
                'display': True,
                'text': 'Completion Time (Last 50 Runs)',
                'fontSize': 16,
                'fontColor': '#ffffff'
            },
            'legend': {
                'display': False
            },
            'scales': {
                'yAxes': [{
                    'ticks': {
                        'beginAtZero': True,
                        'fontColor': '#ffffff'
                    },
                    'gridLines': {
                        'color': 'rgba(255, 255, 255, 0.1)'
                    },
                    'scaleLabel': {
                        'display': True,
                        'labelString': 'Minutes',
                        'fontColor': '#ffffff'
                    }
                }],
                'xAxes': [{
                    'ticks': {
                        'fontColor': '#ffffff',
                        'maxTicksLimit': 10
                    },
                    'gridLines': {
                        'color': 'rgba(255, 255, 255, 0.1)'
                    }
                }]
            }
        }
    }

    chart_config['options']['layout'] = {'padding': 20}
    chart_config['backgroundColor'] = '#2b2d31'

    return generate_quickchart_url(chart_config)


def create_level_line_chart(runs: List[Dict]) -> str:
    """Create a line chart showing level progression over runs."""
    if not runs:
        labels = ['No Data']
        data = [0]
    else:
        labels = [f"Run {i+1}" for i in range(len(runs))]
        # Handle None values as 0
        data = [run['level'] or 0 for run in runs]

    chart_config = {
        'type': 'line',
        'data': {
            'labels': labels,
            'datasets': [{
                'label': 'Level',
                'data': data,
                'borderColor': 'rgba(34, 197, 94, 1)',
                'backgroundColor': 'rgba(34, 197, 94, 0.2)',
                'fill': True,
                'tension': 0.4
            }]
        },
        'options': {
            'title': {
                'display': True,
                'text': 'Level Progress (Last 50 Runs)',
                'fontSize': 16,
                'fontColor': '#ffffff'
            },
            'legend': {
                'display': False
            },
            'scales': {
                'yAxes': [{
                    'ticks': {
                        'fontColor': '#ffffff'
                    },
                    'gridLines': {
                        'color': 'rgba(255, 255, 255, 0.1)'
                    },
                    'scaleLabel': {
                        'display': True,
                        'labelString': 'Level',
                        'fontColor': '#ffffff'
                    }
                }],
                'xAxes': [{
                    'ticks': {
                        'fontColor': '#ffffff',
                        'maxTicksLimit': 10
                    },
                    'gridLines': {
                        'color': 'rgba(255, 255, 255, 0.1)'
                    }
                }]
            }
        }
    }

    chart_config['options']['layout'] = {'padding': 20}
    chart_config['backgroundColor'] = '#2b2d31'

    return generate_quickchart_url(chart_config)


def create_gold_line_chart(runs: List[Dict]) -> str:
    """Create a line chart showing gold earned over runs."""
    if not runs:
        labels = ['No Data']
        data = [0]
    else:
        labels = [f"Run {i+1}" for i in range(len(runs))]
        # Handle None values as 0
        data = [run['rewards_gold'] or 0 for run in runs]

    chart_config = {
        'type': 'line',
        'data': {
            'labels': labels,
            'datasets': [{
                'label': 'Gold',
                'data': data,
                'borderColor': 'rgba(250, 204, 21, 1)',
                'backgroundColor': 'rgba(250, 204, 21, 0.2)',
                'fill': True,
                'tension': 0.4
            }]
        },
        'options': {
            'title': {
                'display': True,
                'text': 'Gold Earned (Last 50 Runs)',
                'fontSize': 16,
                'fontColor': '#ffffff'
            },
            'legend': {
                'display': False
            },
            'scales': {
                'yAxes': [{
                    'ticks': {
                        'beginAtZero': True,
                        'fontColor': '#ffffff'
                    },
                    'gridLines': {
                        'color': 'rgba(255, 255, 255, 0.1)'
                    },
                    'scaleLabel': {
                        'display': True,
                        'labelString': 'Gold',
                        'fontColor': '#ffffff'
                    }
                }],
                'xAxes': [{
                    'ticks': {
                        'fontColor': '#ffffff',
                        'maxTicksLimit': 10
                    },
                    'gridLines': {
                        'color': 'rgba(255, 255, 255, 0.1)'
                    }
                }]
            }
        }
    }

    chart_config['options']['layout'] = {'padding': 20}
    chart_config['backgroundColor'] = '#2b2d31'

    return generate_quickchart_url(chart_config)


def create_gems_line_chart(runs: List[Dict]) -> str:
    """Create a line chart showing gems earned over runs."""
    if not runs:
        labels = ['No Data']
        data = [0]
    else:
        labels = [f"Run {i+1}" for i in range(len(runs))]
        # Handle None values as 0
        data = [run['rewards_gems'] or 0 for run in runs]

    chart_config = {
        'type': 'line',
        'data': {
            'labels': labels,
            'datasets': [{
                'label': 'Gems',
                'data': data,
                'borderColor': 'rgba(168, 85, 247, 1)',
                'backgroundColor': 'rgba(168, 85, 247, 0.2)',
                'fill': True,
                'tension': 0.4
            }]
        },
        'options': {
            'title': {
                'display': True,
                'text': 'Gems Earned (Last 50 Runs)',
                'fontSize': 16,
                'fontColor': '#ffffff'
            },
            'legend': {
                'display': False
            },
            'scales': {
                'yAxes': [{
                    'ticks': {
                        'beginAtZero': True,
                        'fontColor': '#ffffff'
                    },
                    'gridLines': {
                        'color': 'rgba(255, 255, 255, 0.1)'
                    },
                    'scaleLabel': {
                        'display': True,
                        'labelString': 'Gems',
                        'fontColor': '#ffffff'
                    }
                }],
                'xAxes': [{
                    'ticks': {
                        'fontColor': '#ffffff',
                        'maxTicksLimit': 10
                    },
                    'gridLines': {
                        'color': 'rgba(255, 255, 255, 0.1)'
                    }
                }]
            }
        }
    }

    chart_config['options']['layout'] = {'padding': 20}
    chart_config['backgroundColor'] = '#2b2d31'

    return generate_quickchart_url(chart_config)
